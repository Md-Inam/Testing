#---------------------------------------------- Imports ----------------------------------------------
import streamlit as st
import tempfile
from utils import *

#---------------------------------------------- Side Bar (Key) ----------------------------------------------

st.set_page_config(page_title="Chat with SQL Database", page_icon="🌐")

# Create a sidebar for entering the Gemini API key.
with st.sidebar:
    st.markdown("# Enter your Gemini API Key here:")
    gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")
    st.markdown("# Upload your CSV file:")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            csv_path = tmp_file.name

            st.success("CSV file uploaded successfully!")
            # Set up the database and the agent using the temporary CSV file
            engine = setup_database(csv_path, uploaded_file.name)
            if not gemini_api_key:
                st.warning('Please enter your API key!', icon='⚠')
                st.stop()
            agent_executor, query_logger = setup_agent(engine, gemini_api_key)
            st.success("Agent is set up and ready to answer your questions!")
    
    "[🔑 Get your Gemini API key](https://ai.google.dev/gemini-api/docs)"
    "[👨‍💻 View the source code](https://github.com/AnandThirwani8/Agentic-AI-Driven-Chat-with-SQL-Database)"
    "[🤝 Let's Connect](https://www.linkedin.com/in/anandthirwani/)"
    
    st.markdown("---")
    st.markdown("# About")
    st.markdown(
        "🚀 This Text-to-SQL App lets users easily analyze CSV files by asking questions in plain English." 
        "An AI agent creates and runs SQL queries for you and returns both the SQL query and the result."
    )
    st.markdown(
        "You can contribute to the project on [GitHub](https://github.com/AnandThirwani8/Agentic-AI-Driven-Chat-with-SQL-Database) "  
        "with your feedback and suggestions💡"
    )

#---------------------------------------------- Chat UI ----------------------------------------------
# Set up the web application interface.
st.title("🤖💬📊 Chat with SQL Database")
st.caption("🚀 Powered by Google Gemini and Langhchain")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I help you ?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if query := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").write(query)

    # Generate response 
    with st.spinner("Thinking..."):

        if not gemini_api_key or not uploaded_file:
            st.warning('Please enter your API key and upload a csv file !', icon='⚠')
            st.stop()
        else:
            answer, sql_query = get_result(query, agent_executor, query_logger)
        msg = answer

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    st.write("**Generated SQL Query:**")
    formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
    st.code(formatted_sql, language="sql")
