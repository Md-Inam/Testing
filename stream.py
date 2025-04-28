import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from langchain.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI as GenAI
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit UI setup
st.set_page_config(layout="wide", page_title="AI SQL Agent")

# Sidebar for API Key & File Upload
st.sidebar.title("🔑 API Key & File Upload")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Main layout
st.title("🤖 AI-Powered Text-to-SQL Converter")
st.write("Ask questions in plain English and get instant results!")

# If API key and file are uploaded, process the file
if api_key and uploaded_file:
    os.environ["GOOGLE_API_KEY"] = api_key

    # Load CSV into DataFrame
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"⚠️ Error loading file: {str(e)}")
        st.stop()

    # Create SQLite database
    engine = create_engine("sqlite:///uploaded_data.db")
    df.to_sql("uploaded_table", engine=engine, index=False, if_exists='replace')

    # Initialize SQL database
    db = SQLDatabase(engine=engine)

    # Initialize AI Model
    llm = GenAI(model="gemini-1.5-flash", temperature=0, google_api_key=api_key)

    # Create SQL Agent
    agent_executor = create_sql_agent(llm, db=db, verbose=True, return_intermediate_steps=True)

    # Input query
    query = st.text_input("🔍 Enter your question:")

    if query:
        try:
            # AI Processing
            response = agent_executor.invoke({"input": query})

            # Extract generated SQL query
            sql_query = response["intermediate_steps"][0]["query"]

            # Show SQL Query
            st.subheader("📝 Generated SQL Query:")
            st.code(sql_query, language="sql")

            # Show Query Result
            query_result = response.get("output", "⚠️ No result available.")
            st.subheader("📊 Query Result:")
            st.write(query_result)

        except Exception as e:
            st.error(f"⚠️ Error processing query: {str(e)}")

else:
    st.warning("Please enter your Gemini API key and upload a CSV file to proceed.")
