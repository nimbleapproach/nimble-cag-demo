from crewai_tools import NL2SQLTool
import os
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import markdown
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI # Import ChatOpenAI

load_dotenv()


class CAGSystem:
    def __init__(self):
        self.data_paths = [
            "data/menu_philosophies",
            "data/regional_culinary_stories",
            "data/about_us.md"
        ]
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = None
        print("DEBUG: Calling setup_vectorstore...")
        self.setup_vectorstore()
        print(f"DEBUG: After setup_vectorstore, self.collection is: {self.collection}")
        
        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Initialize NL2SQLTool
        db_uri = (
            f'postgresql://{os.getenv("POSTGRES_USER", "bellaterra")}:'
            f'{os.getenv("POSTGRES_PASSWORD", "password")}@'
            f'{os.getenv("DB_HOST", "db")}:'
            f'{os.getenv("DB_PORT", "5432")}/'
            f'{os.getenv("POSTGRES_DB", "bellaterra_db")}'
        )
        self.nl2sql_tool = NL2SQLTool(db_uri=db_uri)
        
        
    def setup_vectorstore(self):
        """Initialize the vector store with markdown documents"""
        # Use OpenAI embeddings
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="bella_terra_menus",
            embedding_function=openai_ef
        )
        print(f"DEBUG: In setup_vectorstore, collection count is: {self.collection.count()}")
        
        # Check if already populated
        if self.collection.count() > 0:
            print(f"DEBUG: Vector store already populated with {self.collection.count()} documents. Returning.")
            return
        
        # Load and process markdown files from specified paths
        documents = []
        metadatas = []
        ids = []

        for path in self.data_paths:
            if os.path.isdir(path):
                for filename in os.listdir(path):
                    if filename.endswith('.md'):
                        file_path = os.path.join(path, filename)
                        self._process_markdown_file(file_path, documents, metadatas, ids)
            elif os.path.isfile(path) and path.endswith('.md'):
                self._process_markdown_file(path, documents, metadatas, ids)

    def _process_markdown_file(self, file_path, documents, metadatas, ids):
        """Helper to process a single markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert markdown to plain text
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()

        # Split into chunks
        chunks = self._split_text(text, chunk_size=1000, overlap=200)

        source_name = os.path.basename(file_path)
        for j, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "source": source_name,
                "chunk_index": j
            })
            ids.append(f"{source_name}_{j}")
        
        # Add to collection
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(documents)} chunks to vector store")
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple text splitter"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def create_agents(self):
        """Create CrewAI agents for the CAG system"""
        
        # Context Analyst Agent
        self.context_analyst = Agent(
            role='Context Analyst',
            goal='Analyze and extract relevant context from the Bella Terra menu knowledge base and determine if SQL queries are needed',
            backstory="""You are an expert at understanding and analyzing restaurant 
            information, menus, and business data. You excel at finding relevant 
            information and understanding relationships between different pieces of data.
            You work with the Bella Terra restaurant's menu data. You can also determine
            if a query requires structured data from the SQL database and delegate to the SQL Query Agent.
            """,
            verbose=True,
            allow_delegation=True, # Allow delegation to SQLQueryAgent
            tools=[],
            llm=self.llm
        )
        
        # SQL Query Agent
        self.sql_query_agent = Agent(
            role='SQL Query Agent',
            goal='Execute SQL queries to retrieve structured menu data like prices, ingredients, and dietary information',
            backstory="""You are a specialized agent capable of converting natural language questions
            into precise SQL queries and executing them against the Bella Terra menu database.
            You provide structured data to other agents for comprehensive response generation.
            """,
            verbose=True,
            allow_delegation=False,
            tools=[self.nl2sql_tool],
            llm=self.llm
        )
        
        # Context Augmenter Agent
        self.context_augmenter = Agent(
            role='Context Augmenter',
            goal='Enhance and expand context with additional insights about menu items and relationships',
            backstory="""You specialize in enriching context by identifying patterns, 
            relationships, and implicit information in restaurant menus. You can infer 
            additional context from existing data and make intelligent connections between
            dishes, ingredients, prices, and categories. You can combine insights from both
            the vector store and structured SQL data.
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Response Generator Agent
        self.response_generator = Agent(
            role='Response Generator',
            goal='Generate comprehensive responses about Bella Terra using augmented context',
            backstory="""You are a master at crafting detailed, accurate, and helpful 
            responses about restaurant menus and offerings. You use all available context 
            to provide the most relevant and complete answers possible about Bella Terra.
            You are adept at synthesizing information from both descriptive knowledge and
            precise structured data.
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the vector store"""
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        contexts = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                contexts.append({
                    'content': doc,
                    'source': results['metadatas'][0][i]['source'] if results['metadatas'] else 'Unknown'
                })
        
        return contexts
    
    def augment_context(self, query: str, initial_context: List[Dict[str, Any]]) -> str:
        """Use agents to augment the retrieved context"""
        
        # Format context for agents
        context_str = "\n\n".join([
            f"From {ctx['source']}:\n{ctx['content']}" 
            for ctx in initial_context
        ])
        
        # Task 1: Determine if SQL query is needed and execute
        sql_query_task = Task(
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
            agent=self.context_analyst
        )

        # Task 2: Execute SQL query if needed
        execute_sql_task = Task(
            description=f"""Based on the output from the Context Analyst, execute the SQL query if needed.
            
            If the Context Analyst output is 'NO_SQL_NEEDED', then return 'NO_SQL_RESULTS'.
            Otherwise, use the natural language question provided by the Context Analyst with the NL2SQLTool to get the results from the database.
            """,
            expected_output="The results from the SQL query, or 'NO_SQL_RESULTS'.",
            agent=self.sql_query_agent,
            context=[sql_query_task]
        )

        # Task 3: Analyze initial context and SQL results
        context_analysis_task = Task(
            description=f"""Analyze the following context pieces from Bella Terra's knowledge base for the query: '{query}'
            
            Context pieces:
            {context_str}
            
            Also consider the SQL query results from the previous task.

            Identify key information, relationships between menu items, price patterns, 
            and any any gaps in the context. Focus on understanding the restaurant's offerings
            and combining insights from both descriptive text and structured data.
            """,
            expected_output="A detailed analysis of the menu context and SQL results with key insights about dishes, prices and categories",
            agent=self.context_analyst,
            context=[execute_sql_task]
        )
        
        # Task 4: Augment context
        augmentation_task = Task(
            description="""Based on the context analysis, augment the information by:
            1. Identifying implicit relationships between menu items, prices, and categories
            2. Inferring additional relevant details about ingredients or preparation methods
            3. Suggesting related menu items or pairings that might be helpful
            4. Highlighting any special patterns, pricing tiers, or menu groupings
            5. Making connections between different menu sections (pizza, pasta, wine, etc.)
            Ensure to incorporate precise details from the SQL results where relevant.
            """,
            expected_output="Enhanced context with additional insights about Bella Terra's offerings, including structured data.",
            agent=self.context_augmenter,
            context=[context_analysis_task]
        )
        
        # Task 5: Generate response
        generation_task = Task(
            description=f"""Using all the analyzed and augmented context about Bella Terra, 
            generate a comprehensive response to the query: '{query}'
            
            Ensure the response is:
            - Accurate to the source menu data and SQL results
            - Enhanced with the augmented insights about relationships and patterns
            - Well-structured and easy to understand
            - Complete with all relevant details including prices where applicable
            - Helpful for someone trying to understand Bella Terra's offerings
            """,
            expected_output="A comprehensive, friendly response about Bella Terra's menu offerings",
            agent=self.response_generator,
            context=[context_analysis_task, augmentation_task]
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
        
        # Create agents if not already created
        if not hasattr(self, 'context_analyst'):
            self.create_agents()
        
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
