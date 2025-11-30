"""Task Routes"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.task import Task
import uuid

router = APIRouter()

class TaskCreate(BaseModel):
    content: str
    description: str = None
    project_id: str
    priority: str = "medium"
    estimated_hours: float = None

class TaskUpdate(BaseModel):
    content: str = None
    description: str = None
    status: str = None
    priority: str = None
    assignee: str = None

@router.get("", response_description="Get all tasks")
async def get_tasks(project_id: str = None, db: AsyncSession = Depends(get_db)):
    """Get all tasks, optionally filtered by project"""
    if project_id:
        result = await db.execute(select(Task).where(Task.project_id == uuid.UUID(project_id)))
    else:
        result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return [t.to_dict() for t in tasks]

@router.post("", response_description="Create new task")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task"""
    db_task = Task(
        content=task.content,
        description=task.description,
        project_id=uuid.UUID(task.project_id),
        priority=task.priority,
        estimated_hours=task.estimated_hours,
        status="To Do",
        created_by="user"
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task.to_dict()

@router.get("/{task_id}", response_description="Get task by ID")
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single task"""
    result = await db.execute(select(Task).where(Task.id == uuid.UUID(task_id)))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()

@router.put("/{task_id}", response_description="Update task")
async def update_task(task_id: str, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """Update a task"""
    result = await db.execute(select(Task).where(Task.id == uuid.UUID(task_id)))
    db_task = result.scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.content:
        db_task.content = task.content
    if task.description:
        db_task.description = task.description
    if task.status:
        db_task.status = task.status
    if task.priority:
        db_task.priority = task.priority
    if task.assignee:
        db_task.assignee = task.assignee
    
    await db.commit()
    await db.refresh(db_task)
    return db_task.to_dict()

@router.delete("/{task_id}", response_description="Delete task")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task"""
    result = await db.execute(select(Task).where(Task.id == uuid.UUID(task_id)))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}
