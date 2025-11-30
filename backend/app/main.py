"""
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db

app = FastAPI(title="Project Management API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes.agent import router as AgentRouter
from app.routes.projects import router as ProjectRouter
from app.routes.tasks import router as TaskRouter
from app.routes.sprints import router as SprintRouter
from app.routes.users import router as UserRouter

app.include_router(AgentRouter, tags=["PM-AI Agent"], prefix="/agent")
app.include_router(ProjectRouter, tags=["Projects"], prefix="/projects")
app.include_router(TaskRouter, tags=["Tasks"], prefix="/tasks")
app.include_router(SprintRouter, tags=["Sprints"], prefix="/sprints")
app.include_router(UserRouter, tags=["Users"], prefix="/users")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.get("/")
async def root():
    return {"message": "Project Management API with PostgreSQL", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "postgresql"}
