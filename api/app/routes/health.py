from fastapi import APIRouter
from datetime import datetime
import os

from ..services.cag_service import cag_service

router = APIRouter()


@router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "CAG System API",
        "cag_initialized": cag_service.is_initialized()
    }


@router.get("/health")
async def health_check():
    """Detailed health check"""
    vector_store_info = cag_service.get_vector_store_info()
    
    health = {
        "status": "healthy" if cag_service.is_initialized() else "unhealthy",
        "timestamp": datetime.now(),
        "checks": {
            "cag_system": cag_service.is_initialized(),
            "openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "vector_store": vector_store_info["available"]
        }
    }
    
    if vector_store_info["available"]:
        health["vector_store_documents"] = vector_store_info["count"]
    
    return health 