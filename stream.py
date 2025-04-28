# app.py (or stream.py) --> You can name it anything (but app.py is more standard)

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
st.sidebar.title("🔑 Enter API Key")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")

# File Uploader
st.sidebar.title("📂 Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# Main layout
st.title("🤖 AI-Powered Text-to-SQL Converter")
st.write("Enter a natural language query, and the AI will generate the SQL command and show the result.")

# If API key and file are uploaded, process the file
if api_key and uploaded_file:
    os.environ["GOOGLE_API_KEY"] = api_key

    # Limit file size check (max ~50MB)
    uploaded_file.seek(0, os.SEEK_END)
    file_size = uploaded_file.tell() / (1024 * 1024)  # Size in MB
    uploaded_file.seek(0)

    if file_size > 50:
        st.error("❌ Uploaded file is too large. Please upload a file smaller than 50MB.")
        st.stop()

    # Load CSV into DataFrame
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"⚠️ Error reading CSV file: {str(e)}")
        st.stop()

    # Create SQLite database
    engine = create_engine("sqlite:///uploaded_data.db")
    df.to_sql("uploaded_table", engine, index=False, if_exists='replace')

    # Initialize SQL database
    db = SQLDatabase(engine=engine)

    # Initialize AI Model
    llm = GenAI(model="gemini-1.5-flash", temperature=0, google_api_key=api_key)

    # Create SQL Agent with intermediate steps
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        return_intermediate_steps=True  # ✅ Important to extract SQL query separately
    )

    # Input query
    query = st.text_input("🔍 Enter your question:")

    if query:
        try:
            response = agent_executor.invoke({"input": query})
            
            # Extract SQL Query
            sql_query = response["intermediate_steps"][0]["query"]

            # Display SQL Query
            st.subheader("📝 Generated SQL Query:")
            st.code(sql_query, language="sql")

            # Display Query Result
            st.subheader("📊 Query Result:")
            st.write(response["output"])

        except Exception as e:
            st.error(f"⚠️ Error while processing query: {str(e)}")

else:
    st.warning("⚠️ Please enter your Gemini API key and upload a CSV file to proceed.")
