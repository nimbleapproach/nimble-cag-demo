import os
from typing import List, Dict, Any
from crewai import Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from api.cag.core.vector_store import VectorStore
from api.cag.agents.context_analyst import ContextAnalystAgent
from api.cag.agents.sql_query_agent import SQLQueryAgent
from api.cag.agents.context_augmenter import ContextAugmenterAgent
from api.cag.agents.response_generator import ResponseGeneratorAgent
from api.cag.tasks.sql_query_task import create_sql_query_task, create_execute_sql_task
from api.cag.tasks.context_analysis_task import create_context_analysis_task
from api.cag.tasks.augmentation_task import create_augmentation_task
from api.cag.tasks.generation_task import create_generation_task

load_dotenv()


class CAGSystem:
    def __init__(self):
        self.data_paths = [
            "data/menu_philosophies",
            "data/regional_culinary_stories",
            "data/about_us.md"
        ]
        
        # Initialize vector store
        self.vector_store = VectorStore(self.data_paths)
        self.collection = self.vector_store.collection
        
        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Initialize database URI
        db_uri = (
            f'postgresql://{os.getenv("POSTGRES_USER", "bellaterra")}:'
            f'{os.getenv("POSTGRES_PASSWORD", "password")}@'
            f'{os.getenv("DB_HOST", "db")}:'
            f'{os.getenv("DB_PORT", "5432")}/'
            f'{os.getenv("POSTGRES_DB", "bellaterra_db")}'
        )
        
        # Initialize agents
        self.context_analyst = None
        self.sql_query_agent = None
        self.context_augmenter = None
        self.response_generator = None
        
    def create_agents(self):
        """Create CrewAI agents for the CAG system"""
        
        # Context Analyst Agent
        self.context_analyst = ContextAnalystAgent(self.llm).agent
        
        # SQL Query Agent
        db_uri = (
            f'postgresql://{os.getenv("POSTGRES_USER", "bellaterra")}:'
            f'{os.getenv("POSTGRES_PASSWORD", "password")}@'
            f'{os.getenv("DB_HOST", "db")}:'
            f'{os.getenv("DB_PORT", "5432")}/'
            f'{os.getenv("POSTGRES_DB", "bellaterra_db")}'
        )
        self.sql_query_agent = SQLQueryAgent(db_uri, self.llm).agent
        
        # Context Augmenter Agent
        self.context_augmenter = ContextAugmenterAgent(self.llm).agent
        
        # Response Generator Agent
        self.response_generator = ResponseGeneratorAgent(self.llm).agent
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the vector store"""
        return self.vector_store.retrieve_context(query, k)
    
    def augment_context(self, query: str, initial_context: List[Dict[str, Any]]) -> str:
        """Use agents to augment the retrieved context"""
        
        # Format context for agents
        context_str = "\n\n".join([
            f"From {ctx['source']}:\n{ctx['content']}" 
            for ctx in initial_context
        ])
        
        # Create agents if not already created
        if not self.context_analyst:
            self.create_agents()
        
        # Task 1: Determine if SQL query is needed and execute
        sql_query_task = create_sql_query_task(query, self.context_analyst)

        # Task 2: Execute SQL query if needed
        execute_sql_task = create_execute_sql_task(self.sql_query_agent)
        execute_sql_task.context = [sql_query_task]

        # Task 3: Analyze initial context and SQL results
        context_analysis_task = create_context_analysis_task(
            query, context_str, self.context_analyst, execute_sql_task
        )
        
        # Task 4: Augment context
        augmentation_task = create_augmentation_task(self.context_augmenter, context_analysis_task)
        
        # Task 5: Generate response
        generation_task = create_generation_task(
            query, self.response_generator, context_analysis_task, augmentation_task
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.context_analyst, self.sql_query_agent, self.context_augmenter, self.response_generator],
            tasks=[sql_query_task, execute_sql_task, context_analysis_task, augmentation_task, generation_task],
            process=Process.sequential,
            verbose=True,
            max_rpm=29 # Set a reasonable RPM limit
        )
        
        result = crew.kickoff()
        return str(result)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main method to process a query through the CAG system"""
        print(f"\n🔍 Processing query: {query}")
        
        # Retrieve initial context
        initial_context = self.retrieve_context(query)
        print(f"\n📚 Retrieved {len(initial_context)} context chunks")
        
        # Augment context and generate response
        augmented_response = self.augment_context(query, initial_context)
        
        return {
            "query": query,
            "initial_context": initial_context,
            "augmented_response": augmented_response
        }


def main():
    # Example usage
    cag = CAGSystem()
    
    # Example queries
    queries = [
        "What pizza options are available and what makes them special?",
        "Can you recommend a wine pairing for pasta?",
        "What are the lunch specials at Bella Terra?"
    ]
    
    for query in queries[:1]:  # Just run one example
        result = cag.process_query(query)
        print("\n" + "="*80)
        print(f"Query: {query}")
        print(f"Response: {result['augmented_response']}")
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
