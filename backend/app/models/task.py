"""Task Model"""

from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.base import BaseModel
import uuid

class Task(Base, BaseModel):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String(500), nullable=False)
    description = Column(String)
    status = Column(String(50), default="To Do")
    priority = Column(String(20), default="medium")
    assignee = Column(String(100))
    due_date = Column(DateTime)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(UUID(as_uuid=True), ForeignKey("sprints.id"), nullable=True)
    
    estimated_hours = Column(Float)
    logged_hours = Column(Float, default=0)
    story_points = Column(Float)
    
    tags = Column(JSON, default=[])
    custom_fields = Column(JSON, default={})
    sub_tasks = Column(JSON, default=[])
    blocked_by = Column(JSON, default=[])
    blocking = Column(JSON, default=[])
    time_entries = Column(JSON, default=[])
    comments = Column(JSON, default=[])
    attachments = Column(JSON, default=[])
    
    is_backlog = Column(Boolean, default=True)
    created_by = Column(String(100))
