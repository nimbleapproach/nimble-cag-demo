from .base_agent import BaseAgent
from crewai_tools import NL2SQLTool


class SQLQueryAgent(BaseAgent):
    """SQL Query Agent for executing database queries"""
    
    def __init__(self, db_uri: str, llm=None):
        super().__init__(llm)
        # Initialize the tool with the database URI
        self.nl2sql_tool = NL2SQLTool(db_uri=db_uri)
        self.agent = self.create_agent(
            role='SQL Query Agent',
            goal='Execute SQL queries to retrieve structured menu data like prices, ingredients, and dietary information',
            backstory="""You are a specialized agent capable of converting natural language questions
            into precise SQL queries and executing them against the Bella Terra menu database.
            You provide structured data to other agents for comprehensive response generation.
            """,
            tools=[self.nl2sql_tool],
            allow_delegation=False
        ) 