from crewai import Task


def create_sql_query_task(query: str, context_analyst_agent) -> Task:
    """Create a task to determine if SQL query is needed and execute it"""
    return Task(
        description=f"""Analyze the user's query: '{query}'
        Your primary goal is to determine if this query requires structured data from the `menu_items` SQL database.
        
        If the query requires structured data (e.g., asking for prices, specific menu items, dietary options, or comparisons based on factual data), 
        you MUST formulate a concise natural language question for the `SQL Query Agent` to execute. 
        This question should be directly usable by the `NL2SQLTool` to generate a SQL query.
        
        Examples of questions requiring SQL:
        - "What is the price of a Margherita pizza?"
        - "Show me all vegetarian pasta dishes."
        - "List all wines under £20."
        - "What are the ingredients of the Funghi Delight pizza?"
        
        If the query DOES NOT require structured data (e.g., asking about restaurant philosophy, general descriptions, or recommendations that don't need specific data points),
        you MUST output the exact string 'NO_SQL_NEEDED'.
        
        Your output must be ONLY the natural language question for the SQL Query Agent, or 'NO_SQL_NEEDED'.
        """,
        expected_output="A natural language question for the SQL Query Agent, or the exact string 'NO_SQL_NEEDED'.",
        agent=context_analyst_agent
    )


def create_execute_sql_task(sql_query_agent) -> Task:
    """Create a task to execute SQL query if needed"""
    return Task(
        description=f"""Based on the output from the Context Analyst, execute the SQL query if needed.
        
        If the Context Analyst output is 'NO_SQL_NEEDED', then return 'NO_SQL_RESULTS'.
        Otherwise, use the natural language question provided by the Context Analyst with the NL2SQLTool to get the results from the database.
        """,
        expected_output="The results from the SQL query, or 'NO_SQL_RESULTS'.",
        agent=sql_query_agent
    ) 