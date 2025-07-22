from .base_agent import BaseAgent


class ContextAugmenterAgent(BaseAgent):
    """Context Augmenter Agent for enhancing context with additional insights"""
    
    def __init__(self, llm=None):
        super().__init__(llm)
        self.agent = self.create_agent(
            role='Context Augmenter',
            goal='Enhance and expand context with additional insights about menu items and relationships',
            backstory="""You specialize in enriching context by identifying patterns, 
            relationships, and implicit information in restaurant menus. You can infer 
            additional context from existing data and make intelligent connections between
            dishes, ingredients, prices, and categories. You can combine insights from both
            the vector store and structured SQL data.
            """,
            allow_delegation=False
        ) 