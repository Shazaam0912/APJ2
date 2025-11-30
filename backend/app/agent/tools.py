"""Tools for PM-AI agent to interact with the project management system"""

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.project import Project
from app.models.task import Task
from app.models.sprint import Sprint
from typing import Dict, Any, List
import time

class AgentTools:
    """Tools for PM-AI agent to interact with the database"""
    
    @staticmethod
    async def create_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project in the database"""
        async with AsyncSessionLocal() as session:
            # Generate unique key with timestamp to avoid duplicates
            base_key = project_data.get("key", project_data.get("name", "PROJ")[:4].upper())
            unique_key = f"{base_key}{int(time.time()) % 10000}"  # Add last 4 digits of timestamp
            
            project = Project(
                name=project_data.get("name"),
                key=unique_key,
                description=project_data.get("description"),
                status="active",
                category=project_data.get("category", "ai-generated"),
                board_config={
                    "columns": {},
                    "column_order": [],
                    "swimlane_group_by": "none"
                },
                members=[]
            )
            
            session.add(project)
            await session.commit()
            await session.refresh(project)
            
            return {
                "_id": str(project.id),
                "id": str(project.id),
                "name": project.name,
                "key": project.key,
                "description": project.description,
                "status": project.status,
                "category": project.category
            }
    
    @staticmethod
    async def create_task(task_data: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Create a new task in the database"""
        async with AsyncSessionLocal() as session:
            task = Task(
                content=task_data.get("name") or task_data.get("content"),
                description=task_data.get("description"),
                status="To Do",
                priority=task_data.get("priority", "medium"),
                assignee=task_data.get("assignee"),
                estimated_hours=task_data.get("estimated_hours"),
                logged_hours=0,
                tags=task_data.get("tags", []),
                custom_fields={},
                project_id=project_id,
                is_backlog=True,
                created_by="pm-ai-agent"
            )
            
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            return {
                "_id": str(task.id),
                "id": str(task.id),
                "content": task.content,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "assignee": task.assignee,
                "project_id": str(task.project_id)
            }
    
    @staticmethod
    async def create_sprint(sprint_data: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Create a new sprint in the database"""
        async with AsyncSessionLocal() as session:
            sprint = Sprint(
                name=sprint_data.get("name"),
                goal=sprint_data.get("description") or sprint_data.get("goal"),
                status="planned",
                project_id=project_id,
                task_ids=[],
                velocity=0
            )
            
            session.add(sprint)
            await session.commit()
            await session.refresh(sprint)
            
            return {
                "_id": str(sprint.id),
                "id": str(sprint.id),
                "name": sprint.name,
                "goal": sprint.goal,
                "status": sprint.status,
                "project_id": str(sprint.project_id)
            }
    
    @staticmethod
    async def get_project_by_id(project_id: str) -> Dict[str, Any]:
        """Retrieve a project by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            return project.to_dict() if project else None
    
    @staticmethod
    async def get_tasks_by_project(project_id: str) -> List[Dict[str, Any]]:
        """Retrieve all tasks for a project"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Task).where(Task.project_id == project_id))
            tasks = result.scalars().all()
            return [task.to_dict() for task in tasks]

    @staticmethod
    async def update_task(task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            await session.commit()
            await session.refresh(task)
            return task.to_dict()

    @staticmethod
    async def delete_task(task_id: str) -> bool:
        """Delete a task"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                return False
            
            await session.delete(task)
            await session.commit()
            return True

    @staticmethod
    async def get_project_health(project_id: str) -> Dict[str, Any]:
        """Analyze project health metrics"""
        async with AsyncSessionLocal() as session:
            # Get tasks
            result = await session.execute(select(Task).where(Task.project_id == project_id))
            tasks = result.scalars().all()
            
            total = len(tasks)
            if total == 0:
                return {"status": "empty", "completion_rate": 0}
            
            completed = sum(1 for t in tasks if t.status == "Done")
            in_progress = sum(1 for t in tasks if t.status == "In Progress")
            
            # Identify overloaded members (simple heuristic: > 5 tasks)
            assignee_counts = {}
            for t in tasks:
                if t.assignee and t.status != "Done":
                    assignee_counts[t.assignee] = assignee_counts.get(t.assignee, 0) + 1
            
            overloaded = [k for k, v in assignee_counts.items() if v > 5]
            
            return {
                "total_tasks": total,
                "completion_rate": int((completed / total) * 100),
                "in_progress": in_progress,
                "overloaded_members": overloaded,
                "burnout_risk": "High" if overloaded else "Low"
            }
