from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import uuid
import asyncio
import os

from ..models import QueryRequest, QueryResponse, JobStatus
from ..services.cag_service import cag_service

router = APIRouter()

# In-memory storage for async jobs (use Redis in production)
jobs: dict[str, JobStatus] = {}


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query synchronously and return the response.
    Note: This can take 10-30 seconds to complete.
    """
    if not cag_service.is_initialized():
        raise HTTPException(status_code=503, detail="CAG System not initialized")
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        start_time = datetime.now()
        
        # Process the query
        result = cag_service.process_query(request.query)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return QueryResponse(
            query=request.query,
            response=result['augmented_response'],
            session_id=request.session_id or str(uuid.uuid4()),
            timestamp=end_time,
            processing_time=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/query/async")
async def process_query_async(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process a query asynchronously. Returns a job ID immediately.
    Use GET /jobs/{job_id} to check status and retrieve results.
    """
    if not cag_service.is_initialized():
        raise HTTPException(status_code=503, detail="CAG System not initialized")
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = JobStatus(job_id=job_id, status="processing")
    
    # Add background task
    background_tasks.add_task(process_query_background, job_id, request)
    
    return {"job_id": job_id, "status": "processing"}


async def process_query_background(job_id: str, request: QueryRequest):
    """Background task to process query"""
    try:
        start_time = datetime.now()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            cag_service.process_query, 
            request.query
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        response = QueryResponse(
            query=request.query,
            response=result['augmented_response'],
            session_id=request.session_id or str(uuid.uuid4()),
            timestamp=end_time,
            processing_time=processing_time
        )
        
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status="completed",
            result=response
        )
    
    except Exception as e:
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status="failed",
            error=str(e)
        )


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Check the status of an async job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id] 