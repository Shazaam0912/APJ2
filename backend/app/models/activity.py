from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from app.models.common import PyObjectId

class ActivityLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    user_name: str
    action: str # created, updated, commented, moved, etc.
    target_type: str # task, project, sprint
    target_id: str
    details: Optional[str] = None
    field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ActivityCreate(BaseModel):
    user_id: str
    user_name: str
    action: str
    target_type: str
    target_id: str
    details: Optional[str] = None
    field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
