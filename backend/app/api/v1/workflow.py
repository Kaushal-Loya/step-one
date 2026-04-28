from fastapi import APIRouter, Depends, HTTPException, status
from app.services.mongo_service import MongoDB, COLLECTION_SESSIONS, COLLECTION_ASSETS
from app.agents.orchestrator import orchestrator
from app.tasks.processing_tasks import process_session_metadata
from app.tasks.selection_tasks import selection_task
from app.tasks.gemini_tasks import generate_linkedin_content_task, generate_instagram_content_task, generate_case_study_task
from app.services.telemetry_service import telemetry_service
from app.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/workflow", tags=["workflow"])

MIN_ASSETS = 50
MAX_ASSETS = 150


@router.post("/process-session/{session_id}")
async def process_session(
    session_id: str,
    user_id: str = None
):
    """Trigger end-to-end processing for a session"""
    db = await MongoDB.get_database()
    
    # Get session
    session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if already processing
    if session.get("status") == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already processing"
        )
    
    # Validate asset count (50-150)
    asset_count = session.get("total_assets", 0)
    if asset_count < MIN_ASSETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session has {asset_count} assets. Minimum {MIN_ASSETS} assets required for processing"
        )
    if asset_count > MAX_ASSETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session has {asset_count} assets. Maximum {MAX_ASSETS} assets allowed"
        )
    
    # Update session status
    db[COLLECTION_SESSIONS].update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": "processing"}}
    )
    
    # Broadcast start
    await telemetry_service.broadcast_processing_update(
        session_id,
        "workflow",
        "started",
        0.0,
        "Starting end-to-end processing"
    )
    
    try:
        # Step 1: Run LangGraph workflow
        workflow_result = orchestrator.run_workflow(session_id)
        
        # Step 2: Queue metadata extraction for all assets
        process_session_metadata.delay(session_id)
        
        # Step 3: Queue selection after metadata
        selection_task.delay(session_id)
        
        # Step 4: Queue content generation after selection
        generate_linkedin_content_task.delay(session_id)
        generate_instagram_content_task.delay(session_id)
        generate_case_study_task.delay(session_id)
        
        # Broadcast completion
        await telemetry_service.broadcast_processing_update(
            session_id,
            "workflow",
            "queued",
            1.0,
            "All tasks queued successfully"
        )
        
        return {
            "session_id": session_id,
            "status": "processing",
            "workflow_result": workflow_result,
            "message": "End-to-end processing initiated"
        }
        
    except Exception as e:
        # Update session status on error
        db[COLLECTION_SESSIONS].update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"status": "failed"}}
        )
        
        await telemetry_service.broadcast_error(
            session_id,
            str(e),
            "workflow"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )


@router.get("/status/{session_id}")
async def get_workflow_status(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get current workflow status for a session"""
    db = await MongoDB.get_database()
    
    # Get session
    session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get processing logs
    from app.services.mongo_service import COLLECTION_LOGS
    logs = list(db[COLLECTION_LOGS].find({"session_id": session_id}).sort("timestamp", -1))
    
    # Get asset count
    asset_count = db[COLLECTION_ASSETS].count_documents({"session_id": session_id})
    
    return {
        "session_id": session_id,
        "status": session.get("status"),
        "asset_count": asset_count,
        "processed_assets": session.get("processed_assets", 0),
        "selection_stats": session.get("metadata", {}).get("selection_stats", {}),
        "recent_logs": [
            {
                "stage": log.get("stage"),
                "status": log.get("status"),
                "timestamp": log.get("timestamp"),
                "duration_ms": log.get("duration_ms")
            }
            for log in logs[:10]
        ]
    }


@router.post("/retry-stage/{session_id}")
async def retry_stage(
    session_id: str,
    stage: str,
    user_id: str = Depends(get_current_user)
):
    """Retry a specific processing stage"""
    db = await MongoDB.get_database()
    
    # Get session
    session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Queue appropriate task based on stage
    if stage == "metadata":
        process_session_metadata.delay(session_id)
    elif stage == "selection":
        selection_task.delay(session_id)
    elif stage == "content_generation":
        generate_linkedin_content_task.delay(session_id)
        generate_instagram_content_task.delay(session_id)
        generate_case_study_task.delay(session_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown stage: {stage}"
        )
    
    await telemetry_service.broadcast_processing_update(
        session_id,
        stage,
        "retrying",
        0.0,
        f"Retrying stage: {stage}"
    )
    
    return {
        "session_id": session_id,
        "stage": stage,
        "status": "retrying"
    }
