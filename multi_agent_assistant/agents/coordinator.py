"""Primary Agent Coordinator - orchestrates sub-agents and workflows"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum
from agents.sub_agents import SubAgentManager
from db.models import Workflow, WorkflowTask, TaskStatus

class WorkflowStep:
    """Represents a step in a workflow"""
    
    def __init__(self, step_id: str, agent_name: str, task_data: Dict[str, Any], 
                 depends_on: List[str] = None):
        self.step_id = step_id
        self.agent_name = agent_name
        self.task_data = task_data
        self.depends_on = depends_on or []
        self.result = None
        self.status = "pending"
        self.error = None

class PrimaryAgentCoordinator:
    """Coordinates multiple sub-agents and manages workflows"""
    
    def __init__(self):
        self.sub_agent_manager = SubAgentManager()
        self.workflows = {}
        self.execution_history = []
    
    async def execute_task(self, agent_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task on a sub-agent"""
        try:
            result = await self.sub_agent_manager.dispatch(agent_name, task_data)
            
            # Log execution
            self.execution_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": agent_name,
                "task": task_data,
                "result": result,
                "status": "success"
            })
            
            return result
        except Exception as e:
            error_result = {
                "agent": agent_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.execution_history.append({
                **error_result,
                "status": "error"
            })
            
            return error_result
    
    async def execute_workflow(self, workflow_id: str, steps: List[WorkflowStep]) -> Dict[str, Any]:
        """Execute a multi-step workflow"""
        workflow_result = {
            "workflow_id": workflow_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "steps": [],
            "status": "in_progress"
        }
        
        executed_steps = {}
        dependencies_met = {step.step_id: False for step in steps}
        
        # Check initial dependencies
        for step in steps:
            if not step.depends_on:
                dependencies_met[step.step_id] = True
        
        while len(executed_steps) < len(steps):
            executed_in_iteration = False
            
            for step in steps:
                if step.step_id in executed_steps:
                    continue
                
                # Check if all dependencies are met
                if all(dep in executed_steps for dep in step.depends_on):
                    dependencies_met[step.step_id] = True
                
                if dependencies_met[step.step_id]:
                    # Replace placeholders in task_data with results from dependencies
                    resolved_task_data = self._resolve_task_data(
                        step.task_data, executed_steps
                    )
                    
                    # Execute the step
                    result = await self.execute_task(step.agent_name, resolved_task_data)
                    
                    step.result = result
                    step.status = "completed" if "error" not in result else "failed"
                    executed_steps[step.step_id] = result
                    
                    workflow_result["steps"].append({
                        "step_id": step.step_id,
                        "agent": step.agent_name,
                        "status": step.status,
                        "result": result
                    })
                    
                    executed_in_iteration = True
            
            if not executed_in_iteration and len(executed_steps) < len(steps):
                workflow_result["status"] = "failed"
                workflow_result["error"] = "Circular dependency or missing step"
                break
        
        workflow_result["end_time"] = datetime.now(timezone.utc).isoformat()
        workflow_result["status"] = "completed" if len(executed_steps) == len(steps) else "failed"
        
        return workflow_result
    
    def _resolve_task_data(self, task_data: Dict[str, Any], 
                          executed_steps: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve placeholders in task data using executed step results"""
        resolved = {}
        
        for key, value in task_data.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Extract reference like ${step_id.result_field}
                ref = value[2:-1]  # Remove ${ and }
                parts = ref.split(".")
                step_id = parts[0]
                
                if step_id in executed_steps:
                    result = executed_steps[step_id]
                    
                    # Navigate through nested structure
                    for part in parts[1:]:
                        if isinstance(result, dict):
                            result = result.get(part)
                        else:
                            result = None
                            break
                    
                    resolved[key] = result if result is not None else value
                else:
                    resolved[key] = value
            elif isinstance(value, dict):
                resolved[key] = self._resolve_task_data(value, executed_steps)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_task_data(item, executed_steps) 
                    if isinstance(item, dict) else item 
                    for item in value
                ]
            else:
                resolved[key] = value
        
        return resolved
    
    async def schedule_workflow(self, workflow_id: str, steps: List[WorkflowStep], 
                                trigger: str = "manual") -> Dict[str, Any]:
        """Schedule a workflow for execution"""
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "steps": steps,
            "trigger": trigger,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "scheduled"
        }
        
        return {
            "workflow_id": workflow_id,
            "status": "scheduled",
            "trigger": trigger,
            "message": f"Workflow {workflow_id} scheduled successfully"
        }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        return {
            "workflow_id": workflow_id,
            **self.workflows[workflow_id]
        }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history[-limit:]
    
    def list_available_agents(self) -> List[str]:
        """List all available sub-agents"""
        return self.sub_agent_manager.list_agents()
    
    async def handle_multi_step_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a multi-step task request"""
        task_type = task.get("type", "simple")
        
        if task_type == "workflow":
            steps = [
                WorkflowStep(
                    step_id=step.get("id"),
                    agent_name=step.get("agent"),
                    task_data=step.get("data"),
                    depends_on=step.get("depends_on", [])
                )
                for step in task.get("steps", [])
            ]
            
            return await self.execute_workflow(
                task.get("workflow_id"),
                steps
            )
        else:
            # Single task
            return await self.execute_task(
                task.get("agent"),
                task.get("data", {})
            )
