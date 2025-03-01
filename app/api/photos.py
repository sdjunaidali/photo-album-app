from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List

from app.schemas.photo import PhotoUpload, PhotoResponse
from app.crud.photos import upload_photo, get_user_photos, get_group_photos, delete_photo
from app.core.database import get_session
from app.core.security import oauth2_scheme
from app.models.user import User
from app.models.photo import Photo
from app.models.group import Group
from app.services.minio_status_codes import MinIOStatusCodes
from app.services.minio_client import upload_to_minio, get_minio_object_url, delete_from_minio
from app.crud.users import create_user, get_user_by_id, get_user_by_email, get_user_in_group, authenticate_user, get_current_user

router = APIRouter(
    tags=["photos"]
)

# Upload a photo
@router.post("/upload/{group_id}", response_model=PhotoResponse)
async def upload_photo_endpoint(
    photo: PhotoUpload, 
    group_id: int,
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Get the current user (admin) details from the token
        current_user = get_current_user(db, token)
        uploaded_photo = upload_photo(db, current_user['id'], group_id, photo)
        return uploaded_photo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get photos uploaded by the current user
@router.get("/", response_model=List[PhotoResponse])
def get_user_photos_endpoint(
    db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
):
    current_user = get_current_user(db, token)
    
    photos = get_user_photos(db, current_user['id'])
    return photos

# Get photos in a group
@router.get("/group/{group_id}", response_model=List[PhotoResponse])
def get_group_photos_endpoint(
    group_id: int, db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
):
    current_user = get_current_user(db, token)
    # Check if user is part of the group
    user_in_group = get_user_in_group(db, current_user['id'], group_id)
    if not user_in_group:
        raise HTTPException(status_code=403, detail="You are not a member of this group.")
    
    photos = get_group_photos(db, group_id)
    return photos

# Delete a photo
@router.delete("/delete/{group_id}/{photo_id}")
def delete_photo_endpoint(
    group_id: int, photo_id: int, db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
):
    try:
        current_user = get_current_user(db, token)
        result = delete_photo(db, group_id, current_user['id'], photo_id)
        return result
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))