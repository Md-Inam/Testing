import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from langchain.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI as GenAI
from langchain_community.agent_toolkits import create_sql_agent

# Streamlit UI setup
st.set_page_config(layout="wide", page_title="AI SQL Agent")

# Sidebar for API Key & File Upload
st.sidebar.title("🔑 Enter API Key")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")

st.sidebar.title("📂 Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# Main layout
st.title("🤖 AI-Powered Text-to-SQL Converter")
st.write("Enter a natural language query, and the AI will generate the SQL command and the result.")

if api_key and uploaded_file:
    os.environ["GOOGLE_API_KEY"] = api_key

    # Limit file size
    uploaded_file.seek(0, os.SEEK_END)
    file_size = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)

    if file_size > 50:
        st.error("❌ File too large. Upload file <50MB.")
        st.stop()

    # Load CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV: {str(e)}")
        st.stop()

    # Save to SQLite
    engine = create_engine("sqlite:///uploaded_data.db")
    df.to_sql("uploaded_table", engine, index=False, if_exists='replace')

    # Connect SQL
    db = SQLDatabase(engine=engine)

    # AI Agent
    llm = GenAI(model="gemini-1.5-flash", temperature=0, google_api_key=api_key)
    agent_executor = create_sql_agent(llm=llm, db=db, verbose=True)

    query = st.text_input("🔍 Enter your question:")

    if query:
        try:
            response = agent_executor.invoke({"input": query})

            # Display Output (only answer available)
            st.subheader("📊 Query Result:")
            st.write(response.get("output", "⚠️ No result available."))

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

else:
    st.warning("⚠️ Please enter your Gemini API key and upload a CSV file.")
