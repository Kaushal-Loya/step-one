from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.mongo_service import MongoDB, COLLECTION_OUTPUTS, COLLECTION_SESSIONS
from app.services.qa_judge import qa_judge
from app.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/evaluate/{output_id}")
async def evaluate_output(
    output_id: str,
    user_id: str = Depends(get_current_user)
):
    """Evaluate a specific output using LLM-as-a-Judge"""
    db = await MongoDB.get_database()
    
    # Get output
    output = db[COLLECTION_OUTPUTS].find_one({"_id": ObjectId(output_id)})
    if not output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output not found"
        )
    
    # Get session for context
    session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(output["session_id"])})
    event_name = session.get("event_name", "") if session else ""
    
    # Evaluate based on output type
    output_type = output.get("output_type")
    content = output.get("content", {})
    
    evaluation = None
    if output_type == "linkedin":
        linkedin_content = content.get("linkedin", {})
        evaluation = qa_judge.evaluate_linkedin_post(
            linkedin_content.get("caption", ""),
            linkedin_content.get("selected_asset_ids", []),
            event_name
        )
    elif output_type == "instagram_reel":
        reel_content = content.get("instagram_reel", {})
        evaluation = qa_judge.evaluate_instagram_content(
            reel_content.get("caption", ""),
            len(content.get("instagram_stories", {}).get("frames", [])),
            event_name
        )
    elif output_type == "case_study":
        evaluation = qa_judge.evaluate_case_study(
            content.get("case_study", {}),
            event_name
        )
    
    # Calculate confidence and check if should flag
    confidence = qa_judge.calculate_confidence_score(evaluation)
    should_flag, reason = qa_judge.should_flag_for_review(evaluation, confidence)
    
    # Update output with evaluation
    db[COLLECTION_OUTPUTS].update_one(
        {"_id": ObjectId(output_id)},
        {"$set": {
            "qa_evaluation": evaluation,
            "confidence_score": confidence,
            "flagged": should_flag,
            "flag_reason": reason if should_flag else None
        }}
    )
    
    return {
        "output_id": output_id,
        "evaluation": evaluation,
        "confidence_score": confidence,
        "flagged": should_flag,
        "flag_reason": reason
    }


@router.post("/evaluate-session/{session_id}")
async def evaluate_session_outputs(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Evaluate all outputs for a session"""
    db = await MongoDB.get_database()
    
    # Get session
    session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get all outputs for session
    outputs = list(db[COLLECTION_OUTPUTS].find({"session_id": session_id}))
    
    # Evaluate all outputs
    results = qa_judge.evaluate_session_outputs(session_id, outputs)
    
    # Update each output with its evaluation
    for eval_result in results["evaluations"]:
        db[COLLECTION_OUTPUTS].update_one(
            {"_id": ObjectId(eval_result["output_id"])},
            {"$set": {
                "qa_evaluation": eval_result["evaluation"],
                "confidence_score": eval_result["confidence_score"],
                "flagged": eval_result["flagged"],
                "flag_reason": eval_result["flag_reason"]
            }}
        )
    
    return results


@router.get("/flagged/{session_id}")
async def get_flagged_outputs(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get all flagged outputs for a session"""
    db = await MongoDB.get_database()
    
    flagged = list(db[COLLECTION_OUTPUTS].find({
        "session_id": session_id,
        "flagged": True
    }))
    
    for output in flagged:
        output["_id"] = str(output["_id"])
    
    return {"session_id": session_id, "flagged_outputs": flagged}


@router.patch("/approve/{output_id}")
async def approve_output(
    output_id: str,
    user_id: str = Depends(get_current_user)
):
    """Manually approve a flagged output"""
    db = await MongoDB.get_database()
    
    result = db[COLLECTION_OUTPUTS].update_one(
        {"_id": ObjectId(output_id)},
        {"$set": {"flagged": False, "flag_reason": None, "manually_approved": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output not found"
        )
    
    return {"output_id": output_id, "status": "approved"}


@router.patch("/reject/{output_id}")
async def reject_output(
    output_id: str,
    reason: str,
    user_id: str = Depends(get_current_user)
):
    """Manually reject an output"""
    db = await MongoDB.get_database()
    
    result = db[COLLECTION_OUTPUTS].update_one(
        {"_id": ObjectId(output_id)},
        {"$set": {
            "flagged": True,
            "flag_reason": f"Manually rejected: {reason}",
            "manually_rejected": True
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output not found"
        )
    
    return {"output_id": output_id, "status": "rejected", "reason": reason}
