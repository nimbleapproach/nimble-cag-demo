from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from ..services.cag_service import cag_service

router = APIRouter()


@router.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    """
    WebSocket endpoint for real-time query processing updates.
    This is a placeholder for future implementation of streaming responses.
    """
    await websocket.accept()
    try:
        while True:
            # Receive query
            data = await websocket.receive_text()
            query_data = json.loads(data)
            
            if not cag_service.is_initialized():
                await websocket.send_json({
                    "type": "error",
                    "message": "CAG System not initialized"
                })
                continue
            
            # Send processing started
            await websocket.send_json({
                "type": "status",
                "message": "Processing query..."
            })
            
            # Process query (in real implementation, you'd stream agent updates)
            try:
                result = cag_service.process_query(query_data["query"])
                await websocket.send_json({
                    "type": "complete",
                    "response": result['augmented_response']
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        print("WebSocket disconnected") 