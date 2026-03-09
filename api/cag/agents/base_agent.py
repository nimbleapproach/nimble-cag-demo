from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import List, Any


class BaseAgent:
    """Base class for all CAG system agents"""
    
    def __init__(self, llm: ChatOpenAI = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.agent = None
    
    def create_agent(self, role: str, goal: str, backstory: str, tools: List[Any] = None, allow_delegation: bool = False) -> Agent:
        """Create a CrewAI agent with common configuration"""
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=allow_delegation,
            tools=tools or [],
            llm=self.llm
        )
    
    def get_agent(self) -> Agent:
        """Get the underlying CrewAI agent"""
        if not self.agent:
            raise ValueError("Agent not created. Call create_agent() first.")
        return self.agent 