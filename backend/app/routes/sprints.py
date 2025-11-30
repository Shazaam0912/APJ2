"""Sprint Routes"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.sprint import Sprint
from datetime import datetime
import uuid

router = APIRouter()

class SprintCreate(BaseModel):
    name: str
    goal: str = None
    project_id: str
    start_date: datetime = None
    end_date: datetime = None

class SprintUpdate(BaseModel):
    name: str = None
    goal: str = None
    status: str = None
    start_date: datetime = None
    end_date: datetime = None

@router.get("", response_description="Get all sprints")
async def get_sprints(project_id: str = None, db: AsyncSession = Depends(get_db)):
    """Get all sprints, optionally filtered by project"""
    if project_id:
        result = await db.execute(select(Sprint).where(Sprint.project_id == uuid.UUID(project_id)))
    else:
        result = await db.execute(select(Sprint))
    sprints = result.scalars().all()
    return [s.to_dict() for s in sprints]

@router.post("", response_description="Create new sprint")
async def create_sprint(sprint: SprintCreate, db: AsyncSession = Depends(get_db)):
    """Create a new sprint"""
    db_sprint = Sprint(
        name=sprint.name,
        goal=sprint.goal,
        project_id=uuid.UUID(sprint.project_id),
        start_date=sprint.start_date,
        end_date=sprint.end_date,
        status="planned"
    )
    db.add(db_sprint)
    await db.commit()
    await db.refresh(db_sprint)
    return db_sprint.to_dict()

@router.get("/{sprint_id}", response_description="Get sprint by ID")
async def get_sprint(sprint_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single sprint"""
    result = await db.execute(select(Sprint).where(Sprint.id == uuid.UUID(sprint_id)))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return sprint.to_dict()

@router.put("/{sprint_id}", response_description="Update sprint")
async def update_sprint(sprint_id: str, sprint: SprintUpdate, db: AsyncSession = Depends(get_db)):
    """Update a sprint"""
    result = await db.execute(select(Sprint).where(Sprint.id == uuid.UUID(sprint_id)))
    db_sprint = result.scalar_one_or_none()
    if not db_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    if sprint.name:
        db_sprint.name = sprint.name
    if sprint.goal:
        db_sprint.goal = sprint.goal
    if sprint.status:
        db_sprint.status = sprint.status
    if sprint.start_date:
        db_sprint.start_date = sprint.start_date
    if sprint.end_date:
        db_sprint.end_date = sprint.end_date
    
    await db.commit()
    await db.refresh(db_sprint)
    return db_sprint.to_dict()

@router.delete("/{sprint_id}", response_description="Delete sprint")
async def delete_sprint(sprint_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a sprint"""
    result = await db.execute(select(Sprint).where(Sprint.id == uuid.UUID(sprint_id)))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    await db.delete(sprint)
    await db.commit()
    return {"message": "Sprint deleted successfully"}
