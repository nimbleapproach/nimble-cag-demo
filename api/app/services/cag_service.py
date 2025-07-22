import sys
import os

# Add the current working directory to Python path so api.cag can be found
sys.path.insert(0, os.getcwd())

from api.cag.core.cag_system import CAGSystem
from typing import Optional


class CAGService:
    """Service class for managing CAG system operations"""
    
    def __init__(self):
        self.cag_system: Optional[CAGSystem] = None
    
    def initialize(self):
        """Initialize the CAG system"""
        try:
            print("🚀 Initializing CAG System with CrewAI agents...")
            self.cag_system = CAGSystem()
            print("✅ CAG System initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize CAG System: {str(e)}")
            self.cag_system = None
            return False
    
    def is_initialized(self) -> bool:
        """Check if CAG system is initialized"""
        return self.cag_system is not None
    
    def process_query(self, query: str):
        """Process a query through the CAG system"""
        if not self.cag_system:
            raise RuntimeError("CAG System not initialized")
        
        return self.cag_system.process_query(query)
    
    def get_vector_store_info(self):
        """Get information about the vector store"""
        if not self.cag_system or not hasattr(self.cag_system, 'collection'):
            return {"count": 0, "available": False}
        
        try:
            count = self.cag_system.collection.count()
            return {"count": count, "available": True}
        except:
            return {"count": 0, "available": False}


# Global CAG service instance
cag_service = CAGService() 