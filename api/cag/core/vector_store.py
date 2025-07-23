import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import markdown
from bs4 import BeautifulSoup


class VectorStore:
    def __init__(self, data_paths: List[str], chroma_path: str = "./chroma_db"):
        self.data_paths = data_paths
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = None
        self.setup_vectorstore()
    
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