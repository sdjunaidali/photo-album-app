from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate
from app.crud.users import get_user_by_email

# Check if a group with the same name already exists
def get_group_by_name(db: Session, name: str):
    return db.query(Group).filter(Group.name == name).first()

# Get group by ID
def get_group_by_id(db: Session, group_id: int) -> Group:
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group

# Create a new group
def create_group(db: Session, group: GroupCreate, admin_id: int):
    existing_group = get_group_by_name(db, name=group.name)
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Group with this name already exists."
        )
    
    new_group = Group(
        name=group.name,
        description=group.description,
        admin_id=admin_id
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    # Add admin as the first member
    new_group.members.append(db.query(User).get(admin_id))
    db.commit()

    return new_group

# Invite a user to a group
def invite_user_to_group(db: Session, current_user_id: int, group_id: int, email: str):
    invited_user = get_user_by_email(db, email=email)
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found."
        )

    group = get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )
    
    # Check if the user is the admin of the group
    if group.admin_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the admin can send invites",
        )
    
    # Check if the user is already a member
    if invited_user in group.members:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this group."
        )
    
    # Add user to group
    group.members.append(invited_user)
    db.commit()
    return {"detail": "User invited successfully."}

# Remove a user from a group
def remove_user_from_group(db: Session, group_id: int, user_id: int, current_user_id: int):
    group = get_group_by_id(db, group_id)

    # Ensure user is a member
    user_to_remove = db.query(User).get(user_id)
    if user_to_remove not in group.members:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this group."
        )

    # Admin can't remove themselves if other members are present
    if group.admin_id == user_id and len(group.members) > 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot remove themselves if other users are present."
        )

    # Check permissions: current user must be the admin or the user themselves
    if current_user_id != group.admin_id and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the admin or the user themselves can remove the user."
        )

    # If admin is last member, delete the group
    if group.admin_id == user_id and len(group.members) == 1:
        db.delete(group)
    else:
        group.members.remove(user_to_remove)
    
    db.commit()
    return {"detail": "User removed successfully."}