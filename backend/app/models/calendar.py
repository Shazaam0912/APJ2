from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.common import PyObjectId

class CalendarEvent(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    start: datetime
    end: datetime
    type: str = "meeting" # meeting, deadline, reminder
    description: Optional[str] = None
    project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CalendarEventCreate(BaseModel):
    title: str
    start: datetime
    end: datetime
    type: str = "meeting"
    description: Optional[str] = None
    project_id: Optional[str] = None

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    type: Optional[str] = None
    description: Optional[str] = None
