import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from langchain.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI as GenAI
from langchain_community.agent_toolkits import create_sql_agent

# Streamlit UI setup
st.set_page_config(layout="wide", page_title="AI SQL Agent")

# Sidebar for Gemini API Key
st.sidebar.title("🔑 API Key & File Upload")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# Main layout
st.title("🤖 AI-Powered Text-to-SQL Converter")
st.write("Ask questions in plain English and get instant results!")

# File size check function
def check_file_size(uploaded_file):
    uploaded_file.seek(0, os.SEEK_END)
    file_size_mb = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)  # Reset pointer
    return file_size_mb

# Handle file upload
if uploaded_file:
    file_size_mb = check_file_size(uploaded_file)
    if file_size_mb > 50:
        st.error(f"⚠️ File too large ({file_size_mb:.2f} MB). Please upload a file smaller than 50MB.")
        st.stop()

    file_extension = uploaded_file.name.split(".")[-1]

    try:
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            st.stop()

        # Clean column names and datatypes
        df.columns = df.columns.str.replace(" ", "_")
        df = df.convert_dtypes()

    except Exception as e:
        st.error(f"⚠️ Error reading file: {str(e)}")
        st.stop()

else:
    # Default sample dataset
    data = {
        "ID": [1, 2, 3, 4, 5],
        "Name": ["Alice", "Bob", "Charlie", "David", "Emma"],
        "Age": [25, 30, 35, 40, 45],
        "Salary": [50000, 60000, 70000, 80000, 90000]
    }
    df = pd.DataFrame(data)
    st.warning("⚠️ No file uploaded. Using default sample dataset.")

# Create SQLite database
engine = create_engine("sqlite:///uploaded_data.db")
try:
    df.to_sql("uploaded_table", con=engine, index=False, if_exists="replace", method="multi")
except Exception as e:
    st.error(f"⚠️ Error while saving data to database: {str(e)}")
    st.stop()

# Initialize SQL database
db = SQLDatabase(engine=engine)

# Create AI Agent
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    llm = GenAI(model="gemini-1.5-flash", temperature=0, google_api_key=api_key)
    agent_executor = create_sql_agent(llm, db=db, verbose=True, return_intermediate_steps=True)
else:
    st.warning("⚠️ No API key provided. AI features disabled.")

# Query Input
query = st.text_input("🔍 Enter your question:")

if query:
    try:
        if api_key:
            # AI SQL Agent Execution
            response = agent_executor.invoke({"input": query})

            # Get SQL query and result
            sql_query = response["intermediate_steps"][0]["query"]
            query_result = response.get("output", "⚠️ No result available.")

            # Display generated SQL query
            st.subheader("📝 Generated SQL Query:")
            st.code(sql_query, language="sql")

            # Display result
            st.subheader("📊 Query Result:")
            st.write(query_result)

        else:
            st.warning("⚠️ AI is disabled. Running fallback mode.")

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
