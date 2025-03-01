from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)

    # Relationship with Group (many-to-many through membership)
    groups = relationship("Group", secondary="user_groups", back_populates="members", cascade="all, delete")

    # Relationship with Photos (one-to-many)
    photos = relationship("Photo", back_populates="owner", cascade="all, delete")

    # Relationship with Groups as an admin (one-to-many)
    admin_group = relationship("Group", back_populates="admin")

# Association table for many-to-many relationship between Users and Groups
user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True)
)