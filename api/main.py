from fastapi import FastAPI
import os
from dotenv import load_dotenv

from api.app.middleware.cors import setup_cors
from api.app.routes import query, health, websocket
from api.app.services.cag_service import cag_service

load_dotenv()

# Use fast mode for development
USE_FAST_MODE = os.getenv("USE_FAST_MODE", "true").lower() == "true"

# Initialize FastAPI app
app = FastAPI(
    title="CAG System API",
    description="Context Augmentation Generation API for Bella Terra Restaurant",
    version="1.0.0"
)

# Configure CORS
setup_cors(app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])


@app.on_event("startup")
async def startup_event():
    """Initialize the CAG system on startup"""
    cag_service.initialize()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
