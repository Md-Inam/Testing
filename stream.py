import os
import pandas as pd
import streamlit as st
import tempfile
from utils import *  # Assuming you have the necessary helper functions in utils.py

# Streamlit UI setup
st.set_page_config(page_title="Chat with SQL Database", page_icon="🌐")

#---------------------------------------------- Sidebar (Key) ----------------------------------------------

# Create a sidebar for entering the Gemini API key.
with st.sidebar:
    st.markdown("# Enter your Gemini API Key here:")
    gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")
    st.markdown("# Upload your CSV file:")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            csv_path = tmp_file.name

        st.success("CSV file uploaded successfully!")

        # Check the first few lines to preview the file
        with open(csv_path, 'r') as f:
            preview = f.readlines()[:5]  # Read the first 5 lines
        st.write("Preview of the file contents:")
        st.write(preview)

        # Try reading the CSV file with different settings
        df = read_csv_with_check(csv_path)
        
        if df is not None:
            # CSV loaded successfully, display the first few rows
            st.success("CSV file loaded successfully!")
            st.write(df.head())  # Display the first few rows of the dataframe
        else:
            st.warning("Unable to process the CSV file.")

#---------------------------------------------- Main Chat UI ----------------------------------------------

# If everything is set up, show the input interface for user queries
if uploaded_file and gemini_api_key:
    st.title("🤖💬📊 Chat with SQL Database")
    st.caption("🚀 Powered by Google Gemini and Langchain")

    # Initialize session state if not present
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How may I help you?"}]

    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Handle user input
    if query := st.chat_input("Ask a question in plain English..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").write(query)

        # Generate response
        with st.spinner("Thinking..."):
            if not gemini_api_key or not uploaded_file:
                st.warning('Please enter your API key and upload a CSV file!', icon='⚠')
                st.stop()
            else:
                answer, sql_query = get_result(query, gemini_api_key, df)  # Assuming get_result is in utils.py

        # Show the assistant's response
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)

        # Display the generated SQL query
        st.write("**Generated SQL Query:**")
        formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
        st.code(formatted_sql, language="sql")
else:
    st.warning("Please enter your Gemini API key and upload a CSV file to proceed.")
