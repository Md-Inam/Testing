from langchain_community.agent_toolkits import create_sql_agent

def get_result(query, gemini_api_key, df):
    try:
        # Initialize the necessary agent for SQL generation
        # Assuming `create_sql_agent` creates a SQL execution agent (not related to the DataFrame)
        agent_executor, query_logger = setup_agent(df, gemini_api_key)

        # Make sure that 'query_logger' and agent execution are managed correctly.
        query_logger.intermediate_steps.clear()  # Clear previous steps, if any

        # Pass the user query through the agent executor to get SQL generation
        response = agent_executor.invoke({"input": query})

        # Extract the SQL query from the agent's response
        if "intermediate_steps" in response:
            sql_query = response["intermediate_steps"][0]["query"]
        else:
            sql_query = response.get("output", "⚠️ No query generated.")
        
        # Return the response and SQL query
        return response["output"], sql_query
    
    except Exception as e:
        # In case of any error, log the error and return a fallback response
        return f"Error: {str(e)}", ""
