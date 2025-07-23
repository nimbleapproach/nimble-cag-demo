from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """Configure CORS middleware for the FastAPI app"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 