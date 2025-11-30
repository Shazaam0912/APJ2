"""Project Model"""

from sqlalchemy import Column, String, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.base import BaseModel
import uuid
import enum

class ProjectStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    on_hold = "on_hold"

class Project(Base, BaseModel):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    key = Column(String(10), nullable=False, unique=True)
    description = Column(String)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.active)
    category = Column(String(100))
    board_config = Column(JSON, default={"columns": {}, "column_order": [], "swimlane_group_by": "none"})
    members = Column(JSON, default=[])
