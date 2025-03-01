from fastapi import APIRouter, Depends, HTTPException
from fastapi import HTTPException, status
from fastapi import UploadFile, Form, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from typing import List, Dict, Union, Optional

from app.core.database import get_session
from app.core.security import oauth2_scheme
from app.models.user import User
from app.models.group import Group
from app.models.photo import Photo
from app.schemas.user import UserBase, UserCreate, UserLogin, UserResponse, Token
from app.schemas.group import GroupCreate, GroupResponse
from app.schemas.photo import PhotoUpload, PhotoResponse
from app.services.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.services.minio_client import upload_to_minio, get_minio_object_url, delete_from_minio
from app.services.minio_status_codes import MinIOStatusCodes
from app.crud.users import create_user, get_user_by_id, get_user_by_email, get_users_in_group, authenticate_user, get_current_user

router = APIRouter(
    tags=["users"]
)

# Register a new user
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_session)):
    # Check if user with email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    # Create the user
    new_user = create_user(db=db, user=user)
    return new_user

# User login
@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_session)):
    # Authenticate user credentials
    db_user = authenticate_user(db, email=user.email, password=user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    # Generate JWT access token
    access_token = create_access_token(data={"sub": db_user.email, "id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user details
@router.get("/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    db_user = get_user_by_email(db, email=current_user["email"])
    return db_user