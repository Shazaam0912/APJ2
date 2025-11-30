"""PM-AI Agent Service - Core logic for project management automation"""

import json
from typing import Dict, Any, List, Optional
from app.agent import client, MODEL, is_agent_enabled
from app.agent.tools import AgentTools
from app.agent.prompts import (
    PLAN_GENERATION_PROMPT,
    TASK_BREAKDOWN_PROMPT,
    ESTIMATION_PROMPT,
    HEALTH_SUMMARY_PROMPT,
    PRIORITIZATION_PROMPT,
    PRIORITIZATION_PROMPT,
    TASK_LIST_GENERATION_PROMPT,
    TASK_MODIFICATION_PROMPT,
    RESPONSE_GENERATION_PROMPT
)

class AgentService:
    """Project Manager AI Agent Service"""
    
    @staticmethod
    async def generate_project_plan(
        brief: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive project plan from a brief"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured. Missing OPENROUTER_API_KEY.")
        
        constraints_str = json.dumps(constraints or {}, indent=2)
        
        prompt = PLAN_GENERATION_PROMPT.format(
            brief=brief,
            constraints=constraints_str
        )
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Project Manager AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Find start and end of JSON object
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                content = content[start:end+1]
            
            plan = json.loads(content)
            return plan
            
        except Exception as e:
            raise ValueError(f"Failed to generate plan: {str(e)}")
    
    @staticmethod
    async def breakdown_task(
        task_description: str,
        level: str = "epic",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Break down a task into subtasks with estimates"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured.")
        
        prompt = TASK_BREAKDOWN_PROMPT.format(
            task_description=task_description,
            level=level,
            context=context or "No additional context"
        )
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Project Manager AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            breakdown = json.loads(content)
            return breakdown
            
        except Exception as e:
            raise ValueError(f"Failed to breakdown task: {str(e)}")
    
    @staticmethod
    async def generate_estimates(
        tasks: List[Dict[str, Any]],
        team_info: Optional[str] = None,
        hourly_rate: float = 100.0
    ) -> Dict[str, Any]:
        """Generate time and cost estimates for tasks"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured.")
        
        tasks_str = json.dumps(tasks, indent=2)
        
        prompt = ESTIMATION_PROMPT.format(
            tasks=tasks_str,
            team_info=team_info or "Standard development team",
            hourly_rate=hourly_rate
        )
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Project Manager AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            estimates = json.loads(content)
            return estimates
            
        except Exception as e:
            raise ValueError(f"Failed to generate estimates: {str(e)}")
    
    @staticmethod
    async def generate_health_summary(
        project_data: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        team: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate weekly project health summary"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured.")
        
        prompt = HEALTH_SUMMARY_PROMPT.format(
            project_data=json.dumps(project_data, indent=2),
            tasks=json.dumps(tasks, indent=2),
            team=json.dumps(team, indent=2)
        )
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Project Manager AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            health = json.loads(content)
            return health
            
        except Exception as e:
            raise ValueError(f"Failed to generate health summary: {str(e)}")
    
    @staticmethod
    async def prioritize_backlog(
        backlog: List[Dict[str, Any]],
        goals: str,
        capacity: Optional[int] = None
    ) -> Dict[str, Any]:
        """Prioritize backlog items based on value and strategy"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured.")
        
        prompt = PRIORITIZATION_PROMPT.format(
            backlog=json.dumps(backlog, indent=2),
            goals=goals,
            capacity=capacity or "Not specified"
        )
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Project Manager AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            prioritization = json.loads(content)
            return prioritization
            
        except Exception as e:
            raise ValueError(f"Failed to prioritize backlog: {str(e)}")
    
    @staticmethod
    async def generate_task_list(
        goal: str,
        context: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        team_members: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate a prioritized list of tasks for a goal"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured.")
        
        history_str = ""
        if history:
            for msg in history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_str += f"{role.upper()}: {content}\n"
        
        team_str = ""
        if team_members:
            for member in team_members:
                name = member.get('name', 'Unknown')
                role = member.get('role', 'No Role')
                mid = member.get('id', 'No ID')
                team_str += f"- {name} (ID: {mid}) - {role}\n"
        
        prompt = TASK_LIST_GENERATION_PROMPT.format(
            goal=goal,
            context=context or "No additional context",
            history=history_str or "No history",
            team_members=team_str or "No team members provided"
        )
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Project Manager AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            task_list = json.loads(content)
            
            # Fallback: If parsing fails but it's a short response, treat as a question
            if not isinstance(task_list, dict) and len(content) < 500:
                 return {"question": content}
                 
            return task_list
            
        except json.JSONDecodeError:
            # Fallback for non-JSON responses (likely clarification questions)
            if len(content) < 500:
                return {"question": content}
            raise ValueError("Failed to parse task list JSON")
        except Exception as e:
            raise ValueError(f"Failed to generate task list: {str(e)}")

    @staticmethod
    async def execute_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generated plan by creating actual database entities"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured.")
        
        # Create the project
        project = await AgentTools.create_project({
            "name": plan.get("project_name"),
            "description": plan.get("overview"),
            "category": "ai-generated"
        })
        
        project_id = project["_id"]
        created_tasks = []
        created_sprints = []
        
        # Create milestones as sprints
        if plan.get("milestones"):
            for milestone in plan["milestones"]:
                sprint = await AgentTools.create_sprint({
                    "name": milestone.get("name"),
                    "description": milestone.get("description"),
                    "goal": milestone.get("description")
                }, project_id)
                created_sprints.append(sprint)
        
        # Create tasks from plan
        tasks_to_create = plan.get("tasks", [])
        if not tasks_to_create and plan.get("epics"):
            # Fallback to epics if no tasks returned
            tasks_to_create = plan.get("epics", [])
            
        for task_data in tasks_to_create:
            task = await AgentTools.create_task({
                "name": task_data.get("name"),
                "description": task_data.get("description"),
                "priority": task_data.get("priority", "medium"),
                "estimated_hours": task_data.get("estimated_hours"),
                "tags": ["ai-generated"]
            }, project_id)
            created_tasks.append(task)
        
        return {
            "success": True,
            "project": project,
            "tasks_created": len(created_tasks),
            "sprints_created": len(created_sprints),
            "project_id": project_id,
            "tasks": created_tasks,
            "sprints": created_sprints
        }

    @staticmethod
    async def modify_task(request: str, project_id: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Interpret and execute a task modification request"""
        if not is_agent_enabled():
            raise ValueError("Agent not configured.")
            
        prompt = TASK_MODIFICATION_PROMPT.format(
            request=request,
            context=context or f"Project ID: {project_id}"
        )
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Project Manager AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)
            
            # Find the task
            tasks = await AgentTools.get_tasks_by_project(project_id)
            target_name = plan.get("target_task_name", "").lower()
            
            target_task = None
            for task in tasks:
                content = (task.get("content") or "").lower()
                description = (task.get("description") or "").lower()
                
                if target_name in content or target_name in description:
                    target_task = task
                    break
            
            if not target_task:
                return {
                    "success": False,
                    "message": f"Could not find task matching '{target_name}'"
                }
            
            action = plan.get("action")
            if action == "update":
                updates = plan.get("updates", {})
                updated_task = await AgentTools.update_task(target_task["id"], updates)
                return {
                    "success": True,
                    "action": "update",
                    "task": updated_task,
                    "message": f"Updated task '{updated_task['content']}'"
                }
            elif action == "delete":
                await AgentTools.delete_task(target_task["id"])
                return {
                    "success": True,
                    "action": "delete",
                    "task": target_task,
                    "message": f"Deleted task '{target_task['content']}'"
                }
            
            return {"success": False, "message": "Unknown action"}
            
        except Exception as e:
            return {"success": False, "message": f"Error modifying task: {str(e)}"}

    @staticmethod
    async def generate_natural_language_response(action: str, result: Dict[str, Any], prompt: str) -> str:
        """Generate a human-like response for an agent action"""
        
        # Format the prompt
        system_prompt = RESPONSE_GENERATION_PROMPT.format(
            action=action,
            result=json.dumps(result, default=str),
            prompt=prompt
        )
        
        try:
            # Call LLM
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.7 
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            try:
                with open("/tmp/agent_error.log", "w") as f:
                    f.write(f"Error: {str(e)}\nPrompt: {system_prompt}")
            except:
                pass
            print(f"Error generating NL response: {e}")
            return "I completed the action, but I'm having trouble summarizing it right now."
