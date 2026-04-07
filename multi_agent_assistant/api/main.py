"""API endpoints for Multi-Agent Productivity Assistant"""
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from agents.coordinator import PrimaryAgentCoordinator, WorkflowStep
from db.models import init_db, get_db, User, Task, Schedule, Note, TaskStatus
import uuid
import os

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Productivity Assistant",
    description="Coordinate multiple AI agents for task, schedule, and note management",
    version="1.0.0"
)

# Initialize coordinator
coordinator = PrimaryAgentCoordinator()

# Pydantic models for API
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 0
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None

class ScheduleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None

class WorkflowStepData(BaseModel):
    id: str
    agent: str
    data: Dict[str, Any]
    depends_on: List[str] = []

class WorkflowExecuteRequest(BaseModel):
    workflow_id: str
    steps: List[WorkflowStepData]

class SimpleTaskRequest(BaseModel):
    agent: str
    action: str
    params: Dict[str, Any]

# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "available_agents": coordinator.list_available_agents()
    }

# Agent endpoints
@app.get("/agents", tags=["Agents"])
async def list_agents():
    """List all available agents"""
    return {
        "agents": coordinator.list_available_agents(),
        "count": len(coordinator.list_available_agents())
    }

@app.post("/tasks", tags=["Tasks"])
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task"""
    task_id = str(uuid.uuid4())
    
    result = await coordinator.execute_task(
        "task",
        {
            "action": "create",
            "params": {
                "title": task.title,
                "description": task.description or "",
                "priority": task.priority,
                "due_date": task.due_date
            }
        }
    )
    
    # Store in database
    db_task = Task(
        id=task_id,
        user_id="default_user",
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        status=TaskStatus.PENDING
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return {
        "task_id": task_id,
        "agent_result": result,
        "database_status": "saved"
    }

@app.get("/tasks", tags=["Tasks"])
async def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """List tasks with optional filters"""
    result = await coordinator.execute_task(
        "task",
        {
            "action": "get",
            "params": {
                "status": status,
                "priority": priority
            }
        }
    )
    
    return result

@app.put("/tasks/{task_id}", tags=["Tasks"])
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task"""
    update_params = {k: v for k, v in task_update.dict().items() if v is not None}
    update_params["task_id"] = task_id
    
    result = await coordinator.execute_task(
        "task",
        {
            "action": "update",
            "params": update_params
        }
    )
    
    # Update in database
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        for key, value in update_params.items():
            if key != "task_id" and hasattr(db_task, key):
                setattr(db_task, key, value)
        db.commit()
    
    return result

@app.post("/tasks/{task_id}/complete", tags=["Tasks"])
async def complete_task(task_id: str):
    """Mark a task as completed"""
    return await coordinator.execute_task(
        "task",
        {
            "action": "complete",
            "params": {"task_id": task_id}
        }
    )

@app.post("/schedules", tags=["Schedules"])
async def create_schedule(schedule: ScheduleCreate):
    """Create a calendar event"""
    schedule_id = str(uuid.uuid4())
    
    result = await coordinator.execute_task(
        "schedule",
        {
            "action": "create",
            "params": {
                "title": schedule.title,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "description": schedule.description or "",
                "location": schedule.location or ""
            }
        }
    )
    
    return {
        "schedule_id": schedule_id,
        "agent_result": result
    }

@app.get("/schedules", tags=["Schedules"])
async def list_schedules(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """List schedules for a date range"""
    if not start_date:
        start_date = datetime.utcnow()
    if not end_date:
        end_date = datetime(start_date.year, start_date.month, start_date.day, 23, 59, 59)
    
    return await coordinator.execute_task(
        "schedule",
        {
            "action": "get",
            "params": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    )

@app.post("/notes", tags=["Notes"])
async def create_note(note: NoteCreate):
    """Create a note"""
    note_id = str(uuid.uuid4())
    
    result = await coordinator.execute_task(
        "notes",
        {
            "action": "create",
            "params": {
                "title": note.title,
                "content": note.content,
                "tags": note.tags or []
            }
        }
    )
    
    return {
        "note_id": note_id,
        "agent_result": result
    }

@app.get("/notes", tags=["Notes"])
async def list_notes(
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """List notes with optional filters"""
    return await coordinator.execute_task(
        "notes",
        {
            "action": "get",
            "params": {
                "tag": tag,
                "search": search
            }
        }
    )

# Workflow endpoints
@app.post("/workflows/execute", tags=["Workflows"])
async def execute_workflow(request: WorkflowExecuteRequest):
    """Execute a multi-step workflow"""
    steps = [
        WorkflowStep(
            step_id=step.id,
            agent_name=step.agent,
            task_data={"action": "execute", "params": step.data},
            depends_on=step.depends_on
        )
        for step in request.steps
    ]
    
    return await coordinator.execute_workflow(request.workflow_id, steps)

@app.post("/workflows/schedule", tags=["Workflows"])
async def schedule_workflow(request: WorkflowExecuteRequest):
    """Schedule a workflow for later execution"""
    steps = [
        WorkflowStep(
            step_id=step.id,
            agent_name=step.agent,
            task_data={"action": "execute", "params": step.data},
            depends_on=step.depends_on
        )
        for step in request.steps
    ]
    
    return await coordinator.schedule_workflow(request.workflow_id, steps)

@app.get("/workflows/{workflow_id}", tags=["Workflows"])
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    return await coordinator.get_workflow_status(workflow_id)

# History endpoints
@app.get("/history", tags=["History"])
async def get_execution_history(limit: int = Query(50, le=500)):
    """Get execution history"""
    return {
        "executions": coordinator.get_execution_history(limit),
        "count": len(coordinator.get_execution_history(limit))
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "name": "Multi-Agent Productivity Assistant API",
        "version": "1.0.0",
        "description": "Coordinate multiple AI agents for productivity",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "agents": "/agents",
            "tasks": "/tasks",
            "schedules": "/schedules",
            "notes": "/notes",
            "workflows": "/workflows"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    """Global exception handler"""
    return {
        "error": str(exc),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
