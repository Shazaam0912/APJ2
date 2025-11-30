"""Sprint Model"""

from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.base import BaseModel
import uuid

class Sprint(Base, BaseModel):
    __tablename__ = "sprints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    goal = Column(String)
    status = Column(String(50), default="planned")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    task_ids = Column(JSON, default=[])
    velocity = Column(Float, default=0)
