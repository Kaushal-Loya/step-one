from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.telemetry_service import telemetry_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time telemetry"""
    await telemetry_service.connect(websocket, session_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages if needed
            data = await websocket.receive_text()
            # Echo back or handle client messages
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        telemetry_service.disconnect(websocket, session_id)


@router.get("/active-sessions")
async def get_active_sessions(user_id: str = Depends(get_current_user)):
    """Get list of sessions with active telemetry connections"""
    return {
        "active_sessions": telemetry_service.get_active_sessions(),
        "count": len(telemetry_service.get_active_sessions())
    }


@router.get("/connections/{session_id}")
async def get_connection_count(session_id: str, user_id: str = Depends(get_current_user)):
    """Get number of active connections for a session"""
    return {
        "session_id": session_id,
        "connection_count": telemetry_service.get_connection_count(session_id)
    }
