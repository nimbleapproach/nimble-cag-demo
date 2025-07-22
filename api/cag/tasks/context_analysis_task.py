from crewai import Task


def create_context_analysis_task(query: str, context_str: str, context_analyst_agent, sql_task) -> Task:
    """Create a task to analyze initial context and SQL results"""
    return Task(
        description=f"""Analyze the following context pieces from Bella Terra's knowledge base for the query: '{query}'
        
        Context pieces:
        {context_str}
        
        Also consider the SQL query results from the previous task.

        Identify key information, relationships between menu items, price patterns, 
        and any any gaps in the context. Focus on understanding the restaurant's offerings
        and combining insights from both descriptive text and structured data.
        """,
        expected_output="A detailed analysis of the menu context and SQL results with key insights about dishes, prices and categories",
        agent=context_analyst_agent,
        context=[sql_task]
    ) 