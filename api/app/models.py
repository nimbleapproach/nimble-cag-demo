from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="The question to ask about Bella Terra")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")


class QueryResponse(BaseModel):
    query: str
    response: str
    session_id: str
    timestamp: datetime
    processing_time: float


class JobStatus(BaseModel):
    job_id: str
    status: str  # "processing", "completed", "failed"
    result: Optional[QueryResponse] = None
    error: Optional[str] = None 