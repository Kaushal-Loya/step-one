from fastapi import APIRouter
from app.api.v1 import process, sessions

router = APIRouter()
router.include_router(process.router, prefix="/process", tags=["Processing"])
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])

# Temporarily disabled - require MongoDB/S3 configuration
# router.include_router(upload.router, tags=["Upload"])
# router.include_router(workflow.router, tags=["Workflow"])
# router.include_router(review.router, tags=["Review"])
# router.include_router(telemetry.router, tags=["Telemetry"])

__all__ = ["router"]
