from .base_agent import BaseAgent


class ContextAnalystAgent(BaseAgent):
    """Context Analyst Agent for analyzing and extracting relevant context"""
    
    def __init__(self, llm=None):
        super().__init__(llm)
        self.agent = self.create_agent(
            role='Context Analyst',
            goal='Analyze and extract relevant context from the Bella Terra menu knowledge base and determine if SQL queries are needed',
            backstory="""You are an expert at understanding and analyzing restaurant 
            information, menus, and business data. You excel at finding relevant 
            information and understanding relationships between different pieces of data.
            You work with the Bella Terra restaurant's menu data. You can also determine
            if a query requires structured data from the SQL database and delegate to the SQL Query Agent.
            """,
            allow_delegation=True
        ) 