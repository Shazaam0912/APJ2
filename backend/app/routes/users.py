"""User Routes"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "member"

class UserUpdate(BaseModel):
    name: str = None
    email: EmailStr = None
    role: str = None
    is_active: bool = None

@router.get("", response_description="Get all users")
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [u.to_dict() for u in users]

@router.post("", response_description="Create new user")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user.to_dict()

@router.get("/{user_id}", response_description="Get user by ID")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single user"""
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()

@router.put("/{user_id}", response_description="Update user")
async def update_user(user_id: str, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Update a user"""
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.name:
        db_user.name = user.name
    if user.email:
        db_user.email = user.email
    if user.role:
        db_user.role = user.role
    if user.is_active is not None:
        db_user.is_active = user.is_active
    
    await db.commit()
    await db.refresh(db_user)
    return db_user.to_dict()

@router.delete("/{user_id}", response_description="Delete user")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a user"""
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}
