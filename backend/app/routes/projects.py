"""Project Routes"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.project import Project
import uuid

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: str = None
    category: str = "software"

class ProjectUpdate(BaseModel):
    name: str = None
    description: str = None
    status: str = None

@router.get("", response_description="Get all projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects"""
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return [p.to_dict() for p in projects]

@router.post("", response_description="Create new project")
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new project"""
    db_project = Project(
        name=project.name,
        key=project.name[:4].upper(),
        description=project.description,
        category=project.category,
        status="active"
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project.to_dict()

@router.get("/{project_id}", response_description="Get project by ID")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single project"""
    result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()

@router.put("/{project_id}", response_description="Update project")
async def update_project(project_id: str, project: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    """Update a project"""
    result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
    db_project = result.scalar_one_or_none()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.name:
        db_project.name = project.name
    if project.description:
        db_project.description = project.description
    if project.status:
        db_project.status = project.status
    
    await db.commit()
    await db.refresh(db_project)
    return db_project.to_dict()

@router.delete("/{project_id}", response_description="Delete project")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a project"""
    result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted successfully"}
