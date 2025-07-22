from .base_agent import BaseAgent


class ResponseGeneratorAgent(BaseAgent):
    """Response Generator Agent for creating comprehensive responses"""
    
    def __init__(self, llm=None):
        super().__init__(llm)
        self.agent = self.create_agent(
            role='Response Generator',
            goal='Generate comprehensive responses about Bella Terra using augmented context',
            backstory="""You are a master at crafting detailed, accurate, and helpful 
            responses about restaurant menus and offerings. You use all available context 
            to provide the most relevant and complete answers possible about Bella Terra.
            You are adept at synthesizing information from both descriptive knowledge and
            precise structured data.
            """,
            allow_delegation=False
        ) 