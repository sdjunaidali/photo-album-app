from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PhotoBase(BaseModel):
    name: str
    file_path: str

class PhotoUpload(PhotoBase):
    group_id: int  # Photo belongs to this group

    class Config:
        orm_mode = True

class PhotoResponse(PhotoBase):
    id: int
    upload_time: datetime
    user_id: int

    class Config:
        orm_mode = True