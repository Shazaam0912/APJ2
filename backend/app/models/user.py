"""User Model"""

from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.base import BaseModel
import uuid

class User(Base, BaseModel):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="member")
    avatar = Column(String)
    is_active = Column(Boolean, default=True)
    preferences = Column(JSON, default={})
