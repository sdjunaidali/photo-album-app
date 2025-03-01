from pydantic import BaseModel
from typing import List, Optional

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: int
    members: List[str]  # List of member names
    admin_id: int

    class Config:
        orm_mode = True