from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    admin_id = Column(Integer, ForeignKey("users.id"))

    # Relationship with Users (many-to-many through user_groups)
    members = relationship("User", secondary="user_groups", back_populates="groups")

    # Relationship with Photos (one-to-many)
    photos = relationship("Photo", back_populates="group")

    # Admin is the user who created the group
    admin = relationship("User", back_populates="admin_group", uselist=False)