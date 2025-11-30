"""
Unified PM-AI Agent API - Single Endpoint for All Capabilities
**Intelligent routing** based on natural language understanding
"""

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.agent.agent_service import AgentService
from app.agent.tools import AgentTools
import re

router = APIRouter()

class UnifiedAgentRequest(BaseModel):
    """Single request model for all agent operations"""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = None

class UnifiedAgentResponse(BaseModel):
    """Unified response with action type and results"""
    success: bool
    action: str
    result: Dict[str, Any]
    message: str
    execution_details: Optional[Dict[str, Any]] = None

@router.post("/execute", response_description="Execute any PM-AI operation from natural language")
async def execute_agent_command(request: UnifiedAgentRequest = Body(...)):
    """
    **Universal PM-AI Endpoint** - Handles all capabilities through natural language
    
    **Supported Operations:**
    - "Create a project for [description]" → Auto-generates full project plan
    - "Add a task to [do something]" → Creates individual task
    - "Break down [task description]" → Generates subtasks
    - "Estimate time for [tasks]" → Provides time/cost estimates
    - "Prioritize my backlog for [project]" → Orders backlog by value
    - "Give me project health for [project]" → Health summary
    
    **Examples:**
    ```
    "Create a mobile app project for food delivery"
    "Add a task to implement user authentication"
    "Break down the payment integration epic"
    "Estimate time for these 5 tasks"
    "Prioritize backlog for maximum ROI"
    "Show me project health summary"
    ```
    """
    try:
        prompt = request.prompt.lower()
        context = request.context or {}
        
        # ============================================
        # INTENT DETECTION & ROUTING
        # ============================================
        print(f"DEBUG: Prompt='{prompt}'")
        
        # 1. PROJECT CREATION
        if any(kw in prompt for kw in ["create project", "new project", "generate plan"]):
            print("DEBUG: Hit Block 1 (Project Creation)")
            plan = await AgentService.generate_project_plan(
                brief=request.prompt,
                constraints=context.get("constraints")
            )
            execution = await AgentService.execute_plan(plan)
            
            result_data = {
                "project": execution.get("project"),
                "tasks_created": execution.get("tasks_created"),
                "sprints_created": execution.get("sprints_created")
            }
            
            nl_response = await AgentService.generate_natural_language_response(
                action="create_project",
                result=result_data,
                prompt=request.prompt
            )
            
            return UnifiedAgentResponse(
                success=True,
                action="create_project",
                result=result_data,
                message=nl_response,
                execution_details=execution
            )
        
        # 2. BULK TASK CREATION (To-Do List)
        elif any(kw in prompt for kw in ["create tasks", "generate tasks", "to do list", "todo list", "tasks for"]):
            print("DEBUG: Hit Block 2 (Bulk Task Creation)")
            if not context.get("project_id"):
                # Fallback: Create a new project if no active project
                plan = await AgentService.generate_project_plan(brief=request.prompt)
                execution = await AgentService.execute_plan(plan)
                
                result_data = {
                    "project": execution.get("project"),
                    "tasks_created": execution.get("tasks_created"),
                    "sprints_created": execution.get("sprints_created")
                }
                
                nl_response = await AgentService.generate_natural_language_response(
                    action="create_project",
                    result=result_data,
                    prompt=request.prompt
                )
                
                return UnifiedAgentResponse(
                    success=True,
                    action="create_project",
                    result=result_data,
                    message=nl_response,
                    execution_details=execution
                )
            
            # Fetch project details for context
            project_details = await AgentTools.get_project_by_id(context['project_id'])
            project_context = f"Project: {project_details['name']}\nDescription: {project_details['description']}" if project_details else f"Project ID: {context['project_id']}"

            task_list = await AgentService.generate_task_list(
                goal=request.prompt,
                context=project_context,
                history=request.history,
                team_members=context.get("team_members")
            )
            
            # Check for clarification question
            if task_list.get("question"):
                return UnifiedAgentResponse(
                    success=True,
                    action="clarification_needed",
                    result={"question": task_list["question"]},
                    message=task_list["question"]
                )
            
            created_tasks = []
            for task_data in task_list.get("tasks", []):
                description = task_data.get("description", "")
                reasoning = task_data.get("assignment_reasoning")
                if reasoning:
                    description += f"\n\n**🤖 AI Reasoning:** {reasoning}"

                task = await AgentTools.create_task({
                    "name": task_data.get("name"),
                    "description": description,
                    "priority": task_data.get("priority", "medium"),
                    "estimated_hours": task_data.get("estimated_hours"),
                    "assignee": task_data.get("assignee"),
                    "tags": ["ai-generated"]
                }, context["project_id"])
                
                # Handle subtasks
                if task_data.get("sub_tasks"):
                    for sub_name in task_data["sub_tasks"]:
                        await AgentTools.create_task({
                            "name": sub_name,
                            "parent_id": task["id"],
                            "priority": task_data.get("priority", "medium"),
                            "tags": ["ai-generated", "subtask"]
                        }, context["project_id"])
                
                created_tasks.append(task)
            
                result_data = {"tasks": created_tasks}
                
                nl_response = await AgentService.generate_natural_language_response(
                    action="create_tasks",
                    result=result_data,
                    prompt=request.prompt
                )
                
                return UnifiedAgentResponse(
                    success=True,
                    action="create_tasks",
                    result=result_data,
                    message=nl_response,
                    execution_details={"tasks_created": len(created_tasks)}
                )

        # 3. TASK MODIFICATION (Update/Delete)
        elif any(kw in prompt for kw in ["update", "change", "move", "delete", "remove", "reassign"]):
            print("DEBUG: Hit Block 3 (Task Modification)")
            if not context.get("project_id"):
                raise HTTPException(status_code=400, detail="Project ID required for task modification")
            
            result = await AgentService.modify_task(
                request=request.prompt,
                project_id=context["project_id"],
                context=f"Project ID: {context['project_id']}"
            )
            
            nl_response = await AgentService.generate_natural_language_response(
                action=result.get("action", "modify_task"),
                result=result,
                prompt=request.prompt
            )
            
            return UnifiedAgentResponse(
                success=result["success"],
                action=result.get("action", "modify_task"),
                result=result,
                message=nl_response
            )

        # 4. PROJECT HEALTH (Status/Insights)
        elif any(kw in prompt for kw in ["health", "status", "how is the project", "progress", "burnout"]):
            print("DEBUG: Hit Block 4 (Project Health)")
            if not context.get("project_id"):
                raise HTTPException(status_code=400, detail="Project ID required for health check")
            
            health = await AgentTools.get_project_health(context["project_id"])
            
            summary = f"Project Health:\n"
            summary += f"- Completion Rate: {health['completion_rate']}%\n"
            summary += f"- In Progress: {health['in_progress']} tasks\n"
            if health['overloaded_members']:
                summary += f"- ⚠️ Overloaded Members: {', '.join(health['overloaded_members'])}\n"
                summary += f"- Burnout Risk: {health['burnout_risk']}"
            else:
                summary += "- Team Workload: Balanced"
            
            nl_response = await AgentService.generate_natural_language_response(
                action="project_health",
                result=health,
                prompt=request.prompt
            )
            
            return UnifiedAgentResponse(
                success=True,
                action="project_health",
                result=health,
                message=nl_response
            )

        # 5. SINGLE TASK CREATION
        elif any(kw in prompt for kw in ["add task", "create task", "new task", "task for", "create a task", "add a task"]):
            print("DEBUG: Hit Block 5 (Single Task Creation)")
            if not context.get("project_id"):
                raise HTTPException(400, "Project ID required in context for task creation")
            
            # Fetch project details for context
            project_details = await AgentTools.get_project_by_id(context['project_id'])
            project_context = f"Project: {project_details['name']}\nDescription: {project_details['description']}" if project_details else f"Project ID: {context['project_id']}"

            # Use smart generation even for single tasks
            task_list = await AgentService.generate_task_list(
                goal=request.prompt,
                context=project_context,
                history=request.history,
                team_members=context.get("team_members")
            )
            
            created_tasks = []
            for task_data in task_list.get("tasks", []):
                description = task_data.get("description", "")
                reasoning = task_data.get("assignment_reasoning")
                if reasoning:
                    description += f"\n\n**🤖 AI Reasoning:** {reasoning}"

                task = await AgentTools.create_task({
                    "name": task_data.get("name"),
                    "description": description,
                    "priority": task_data.get("priority", "medium"),
                    "estimated_hours": task_data.get("estimated_hours"),
                    "assignee": task_data.get("assignee"),
                    "tags": ["ai-generated"]
                }, context["project_id"])
                
                # Handle subtasks
                if task_data.get("sub_tasks"):
                    for sub_name in task_data["sub_tasks"]:
                        await AgentTools.create_task({
                            "name": sub_name,
                            "parent_id": task["id"],
                            "priority": task_data.get("priority", "medium"),
                            "tags": ["ai-generated", "subtask"]
                        }, context["project_id"])
                
                created_tasks.append(task)
            
            result_data = {"tasks": created_tasks}
            
            nl_response = await AgentService.generate_natural_language_response(
                action="create_task",
                result=result_data,
                prompt=request.prompt
            )
            
            return UnifiedAgentResponse(
                success=True,
                action="create_task",
                result=result_data,
                message=nl_response
            )
        
        # 3. TASK BREAKDOWN
        elif any(kw in prompt for kw in ["break down", "breakdown", "split", "subtasks for"]):
            breakdown = await AgentService.breakdown_task(
                task_description=request.prompt,
                level=context.get("level", "epic"),
                context=context.get("additional_context")
            )
            
            return UnifiedAgentResponse(
                success=True,
                action="breakdown_task",
                result={"breakdown": breakdown},
                message=f"Generated {len(breakdown.get('subtasks', []))} subtasks"
            )
        
        # 4. TIME & COST ESTIMATION
        elif any(kw in prompt for kw in ["estimate", "how long", "time needed", "cost"]):
            tasks = context.get("tasks", [])
            if not tasks:
                return UnifiedAgentResponse(
                    success=False,
                    action="estimate",
                    result={},
                    message="Please provide tasks in context for estimation"
                )
            
            estimates = await AgentService.generate_estimates(
                tasks=tasks,
                team_info=context.get("team_info"),
                hourly_rate=context.get("hourly_rate", 100.0)
            )
            
            return UnifiedAgentResponse(
                success=True,
                action="generate_estimates",
                result={"estimates": estimates},
                message=f"Generated estimates for {len(tasks)} tasks"
            )
        
        # 5. BACKLOG PRIORITIZATION
        elif any(kw in prompt for kw in ["prioritize", "priority", "order backlog", "rank"]):
            if not context.get("project_id"):
                raise HTTPException(400, "Project ID required for backlog prioritization")
            
            backlog = context.get("backlog", [])
            goals = context.get("goals", request.prompt)
            
            prioritization = await AgentService.prioritize_backlog(
                backlog=backlog,
                goals=goals,
                capacity=context.get("capacity")
            )
            
            return UnifiedAgentResponse(
                success=True,
                action="prioritize_backlog",
                result={"prioritization": prioritization},
                message=f"Prioritized {len(backlog)} backlog items"
            )
        
        # 6. PROJECT HEALTH SUMMARY
        elif any(kw in prompt for kw in ["health", "status", "summary", "how is", "progress"]):
            if not context.get("project_id"):
                raise HTTPException(400, "Project ID required for health summary")
            
            # This would call the health summary service
            # For now, return a placeholder
            return UnifiedAgentResponse(
                success=True,
                action="health_summary",
                result={"health": "Feature coming soon"},
                message="Project health summary"
            )
        
        # DEFAULT: GENERAL PROJECT PLAN GENERATION
        else:
            plan = await AgentService.generate_project_plan(brief=request.prompt)
            execution = await AgentService.execute_plan(plan)
            
            result_data = {
                "project": execution.get("project"),
                "tasks_created": execution.get("tasks_created")
            }
            
            nl_response = await AgentService.generate_natural_language_response(
                action="generate_plan",
                result=result_data,
                prompt=request.prompt
            )
            
            return UnifiedAgentResponse(
                success=True,
                action="generate_plan",
                result=result_data,
                message=nl_response,
                execution_details=execution
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities", response_description="List all agent capabilities")
async def get_capabilities():
    """Returns all available PM-AI capabilities"""
    return {
        "capabilities": [
            {
                "name": "Project Generation",
                "description": "Auto-generate complete project plans from briefs",
                "keywords": ["create project", "new project", "build", "develop"],
                "example": "Create a mobile fitness tracking app"
            },
            {
                "name": "Task Creation",
                "description": "Create individual tasks from descriptions",
                "keywords": ["add task", "create task", "new task"],
                "example": "Add a task to implement user authentication"
            },
            {
                "name": "Task Breakdown",
                "description": "Break high-level tasks into subtasks",
                "keywords": ["break down", "breakdown", "split", "subtasks"],
                "example": "Break down the payment integration epic"
            },
            {
                "name": "Estimation",
                "description": "Generate time and cost estimates",
                "keywords": ["estimate", "how long", "time needed", "cost"],
                "example": "Estimate time for implementing auth system"
            },
            {
                "name": "Backlog Prioritization",
                "description": "Prioritize backlog items by value/impact",
                "keywords": ["prioritize", "priority", "order", "rank"],
                "example": "Prioritize my backlog for Q1"
            },
            {
                "name": "Health Summary",
                "description": "Generate project health reports",
                "keywords": ["health", "status", "summary", "progress"],
                "example": "How is the mobile app project doing?"
            }
        ]
    }


@router.get("/status")
async def agent_status():
    """Check if PM-AI agent is operational"""
    from app.agent import is_agent_enabled, MODEL
    
    return {
        "enabled": is_agent_enabled(),
        "model": MODEL if is_agent_enabled() else None,
        "endpoint": "/agent/execute",
        "capabilities_count": 6
    }
