from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.models.user import User, user_groups
from app.models.group import Group
from app.schemas.user import UserCreate
from app.services.auth import hash_password, verify_password, decode_access_token

# Create a new user
def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get user by email
def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

# Get user by ID
def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Authenticate user during login
def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_user_in_group(db: Session, user_id: int, group_id: int):
    return db.query(User).join(Group.members).filter(Group.id == group_id, User.id == user_id).first()

# Get all users in a specific group
def get_users_in_group(db: Session, group_id: int):
    return db.query(User).join(user_groups).filter(user_groups.group_id == group_id).all()

# Dependency to get the current user
def get_current_user(db: Session, token: str):

    user_data = decode_access_token(token)
    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    print(user_data)

    user = db.query(User).filter(User.id == user_data["id"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found or unauthorized")

    return {"email": user.email, "id": user.id}