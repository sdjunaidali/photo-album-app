from fastapi import HTTPException, status
from fastapi import UploadFile, Depends
from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import User
from app.models.photo import Photo
from app.schemas.photo import PhotoUpload, PhotoResponse
from app.crud.users import get_current_user
from app.services.minio_client import upload_to_minio, get_minio_object_url, delete_from_minio
from app.services.minio_status_codes import MinIOStatusCodes
from app.core.config import settings
from app.core.security import oauth2_scheme

async def handle_image_upload(image_data: bytes, image_name: str, user_id: int, group_id: int) -> str:
    """
    Handles uploading an image to MinIO.

    :param image_data: The image file data in bytes.
    :param image_name: Name of the image.
    :param user_id: The ID of the user uploading the image.
    :param group_id: ID of the group image is getting uploaded.
    :return: The URL of the uploaded image.
    :raises Exception: If the upload fails.
    """
    bucket_name = settings.minio_bucket_name
    object_name = f"{group_id}_{user_id}_{image_name}"

    try:
        # Attempt to upload the image
        result = upload_to_minio(image_data, bucket_name, object_name)

        # Handle successful or already existing objects
        if result in [MinIOStatusCodes.SUCCESS, MinIOStatusCodes.OBJECT_ALREADY_EXIST]:
            return get_minio_object_url(bucket_name, object_name)

        # If upload fails, raise an exception with a descriptive message
        raise Exception(f"Failed to upload image. Status code: {result}")
    except Exception as e:
        # Propagate the exception with additional context if needed
        raise Exception(f"Error during image upload: {str(e)}") from e
    

async def upload_photo(db: Session, user_id: int, group_id: int, image: UploadFile) -> PhotoResponse:

    # Check if the group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if the user is part of the group
    if group not in user.groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this group"
        )
    
    # Upload the photo to MinIO
    image_data = await image.read()
    image_name = image.name
    try:
        image_url = await handle_image_upload(image_data, image_name, user_id, group_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload the photo"
        )
    
    # If the upload is successful, create a new photo record
    new_photo = Photo(
        name=image.name,
        file_path=image_url,
        user_id=user_id,
        group_id=group_id
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo

# Get all photos for a user
def get_user_photos(db: Session, user_id: int):
    return db.query(Photo).filter(Photo.user_id == user_id).all()

# Get all photos for a group
def get_group_photos(db: Session, group_id: int):
    return db.query(Photo).filter(Photo.group_id == group_id).all()

# Get photo by ID
def get_photo_by_id(db: Session, photo_id: int) -> Photo:
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    return photo

# Delete a photo (only the uploader or the admin can delete)
def delete_photo(db: Session, group_id: int, user_id: int, photo_id: int):
    # Get photo details
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise ValueError("Photo not found.")
    
    # Check if the user is the owner of the photo or an admin of the group
    if photo.user_id != user_id and not db.query(Group).filter(Group.id == photo.group_id, Group.admin_id == user_id).first():
        raise PermissionError("You do not have permission to delete this photo.")

    # Delete from MinIO
    bucket_name = settings.minio_bucket_name
    object_name = f"{group_id}_{user_id}_{photo.name}"
    delete_status = delete_from_minio(settings.minio_bucket_name, object_name)
    
    if delete_status != MinIOStatusCodes.SUCCESS:
        raise Exception(f"Failed to delete photo from MinIO: {MinIOStatusCodes.get_status_description(delete_status)}")

    # Delete from database
    db.delete(photo)
    db.commit()

    return {"message": "Photo deleted successfully"}