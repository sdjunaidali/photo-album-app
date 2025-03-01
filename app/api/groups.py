from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate, GroupResponse
from app.crud.groups import create_group, get_group_by_id, invite_user_to_group, remove_user_from_group
from app.crud.users import get_user_by_id, get_current_user
from app.core.security import oauth2_scheme

router = APIRouter(
    tags=["groups"]
)

# Create a new group
@router.post("/", response_model=GroupResponse)
def create_new_group(group: GroupCreate, db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    # Get the current user (admin) details from the token
    current_user = get_current_user(db, token)
    admin_id = current_user['id']
    
    # Create the group
    new_group = create_group(db, group=group, admin_id=admin_id)
    return new_group

# Get group by ID
@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_session)):
    group = get_group_by_id(db, group_id)
    return group

# Invite a user to a group
@router.post("/{group_id}/invite", status_code=status.HTTP_200_OK)
def invite_user_to_group_route(group_id: int, email: str, db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    # Get the current user (admin) details from the token
    current_user = get_current_user(db, token)
    
    # Invite the user to the group
    result = invite_user_to_group(db, current_user['id'], group_id, email)
    return {"detail": "User invited successfully."}

# Remove a user from a group
@router.delete("/{group_id}/remove/{user_id}", status_code=status.HTTP_200_OK)
def remove_user_from_group_route(group_id: int, user_id: int, db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    # Get the current user (admin) details from the token
    current_user = get_current_user(db, token)
    current_user_id = current_user['id']
    
    # Remove the user from the group
    result = remove_user_from_group(db, group_id, user_id, current_user_id)
    return result