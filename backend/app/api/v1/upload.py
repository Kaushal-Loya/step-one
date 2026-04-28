from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from app.services.s3_service import s3_service
from app.services.mongo_service import MongoDB, COLLECTION_SESSIONS, COLLECTION_ASSETS
from app.models.asset import Asset, AssetCreate, FileType, Orientation
from app.dependencies import get_current_user
from bson import ObjectId
import uuid
import os

router = APIRouter(prefix="/upload", tags=["upload"])

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"
}
ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"
}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
MIN_ASSETS = 50
MAX_ASSETS = 150


@router.post("/presigned-url")
async def generate_upload_url(
    session_id: str,
    filename: str,
    content_type: str,
    user_id: str = Depends(get_current_user)
):
    """Generate a presigned URL for direct S3 upload"""
    
    # Validate file type
    if content_type not in ALLOWED_IMAGE_TYPES and content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES}"
        )
    
    # Check if session exists and belongs to user
    db = await MongoDB.get_database()
    session = await db[COLLECTION_SESSIONS].find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Generate presigned URL
    result = s3_service.generate_upload_url(session_id, filename, content_type)
    
    return {
        "upload_url": result["upload_url"],
        "file_key": result["file_key"],
        "expires_in": result["expires_in"]
    }


@router.post("/{session_id}/files")
async def upload_files(
    session_id: str,
    files: List[UploadFile] = File(...),
    user_id: str = None
):
    """Upload files directly to the server (alternative to presigned URL)"""
    
    # Check if session exists
    db = await MongoDB.get_database()
    user_id = user_id or "dev_user"
    session = await db[COLLECTION_SESSIONS].find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check current asset count
    current_count = session.get("total_assets", 0)
    new_files_count = len(files)
    total_after_upload = current_count + new_files_count
    
    # Validate asset count range (50-150)
    if total_after_upload > MAX_ASSETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upload {new_files_count} files. Session would have {total_after_upload} assets, exceeding maximum of {MAX_ASSETS}"
        )
    
    uploaded_assets = []
    
    for file in files:
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File {file.filename} exceeds maximum size of 500MB"
            )
        
        # Validate file type
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_IMAGE_TYPES and content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type for {file.filename}"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        object_key = f"sessions/{session_id}/{unique_filename}"
        
        # Upload to S3
        try:
            s3_service.s3_client.upload_fileobj(
                file.file,
                s3_service.bucket,
                object_key,
                ExtraArgs={'ContentType': content_type}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file.filename}: {str(e)}"
            )
        
        # Determine file type and orientation
        if content_type in ALLOWED_IMAGE_TYPES:
            file_type = FileType.IMAGE
            # For now, default to landscape - will be updated during metadata extraction
            orientation = Orientation.LANDSCAPE
        else:
            file_type = FileType.VIDEO
            orientation = Orientation.LANDSCAPE
        
        # Create asset record
        asset_data = {
            "session_id": session_id,
            "original_filename": file.filename,
            "s3_key": object_key,
            "s3_url": s3_service.get_file_url(object_key, expiration=86400),
            "file_type": file_type,
            "format": file_extension.lstrip('.'),
            "size_bytes": file_size,
            "dimensions": {"width": 0, "height": 0},  # Will be updated during metadata extraction
            "orientation": orientation,
            "metadata": {}
        }
        
        result = await db[COLLECTION_ASSETS].insert_one(asset_data)
        asset_data["_id"] = str(result.inserted_id)
        uploaded_assets.append(asset_data)
    
    # Update session asset count
    await db[COLLECTION_SESSIONS].update_one(
        {"_id": ObjectId(session_id)},
        {"$inc": {"total_assets": len(uploaded_assets)}}
    )
    
    return {
        "uploaded_count": len(uploaded_assets),
        "session_id": session_id,
        "assets": uploaded_assets,
        "total_assets": total_after_upload,
        "min_required": MIN_ASSETS,
        "max_allowed": MAX_ASSETS
    }


@router.post("/{session_id}/confirm-upload")
async def confirm_upload(
    session_id: str,
    file_key: str,
    filename: str,
    content_type: str,
    file_size: int,
    user_id: str = None
):
    """Confirm that a file was uploaded via presigned URL and create asset record"""
    
    # Check if session exists
    db = await MongoDB.get_database()
    user_id = user_id or "dev_user"
    session = await db[COLLECTION_SESSIONS].find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check current asset count
    current_count = session.get("total_assets", 0)
    total_after_upload = current_count + 1
    
    # Validate asset count range (50-150)
    if total_after_upload > MAX_ASSETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upload file. Session would have {total_after_upload} assets, exceeding maximum of {MAX_ASSETS}"
        )
    
    # Verify file exists in S3
    if not s3_service.file_exists(file_key):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in S3"
        )
    
    # Determine file type
    if content_type in ALLOWED_IMAGE_TYPES:
        file_type = FileType.IMAGE
        orientation = Orientation.LANDSCAPE
    else:
        file_type = FileType.VIDEO
        orientation = Orientation.LANDSCAPE
    
    # Create asset record
    asset_data = {
        "session_id": session_id,
        "original_filename": filename,
        "s3_key": file_key,
        "s3_url": s3_service.get_file_url(file_key, expiration=86400),
        "file_type": file_type,
        "format": os.path.splitext(filename)[1].lstrip('.'),
        "size_bytes": file_size,
        "dimensions": {"width": 0, "height": 0},
        "orientation": orientation,
        "metadata": {}
    }
    
    result = await db[COLLECTION_ASSETS].insert_one(asset_data)
    asset_data["_id"] = str(result.inserted_id)
    
    # Update session asset count
    await db[COLLECTION_SESSIONS].update_one(
        {"_id": ObjectId(session_id)},
        {"$inc": {"total_assets": 1}}
    )
    
    return {
        "asset_id": result.inserted_id,
        "status": "confirmed"
    }
