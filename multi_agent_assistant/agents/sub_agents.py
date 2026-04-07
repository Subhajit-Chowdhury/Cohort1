"""Sub-agents for specialized task handling"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import datetime, timezone
from mcp_tools.tools import MCPToolFactory

class SubAgent(ABC):
    """Base class for sub-agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.context = {}
    
    @abstractmethod
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task"""
        pass
    
    def set_context(self, key: str, value: Any):
        """Set context for the agent"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self.context.get(key, default)

class TaskAgent(SubAgent):
    """Agent for managing tasks"""
    
    def __init__(self):
        super().__init__("TaskAgent")
        self.tool = MCPToolFactory.get_tool("task_manager")
    
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task-related requests"""
        action = task_data.get("action", "create")
        
        result = await self.tool.execute(action, **task_data.get("params", {}))
        
        return {
            "agent": self.name,
            "action": action,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_task(self, title: str, **kwargs) -> Dict[str, Any]:
        """Create a task"""
        return await self.process({
            "action": "create",
            "params": {"title": title, **kwargs}
        })
    
    async def get_tasks(self, **filters) -> Dict[str, Any]:
        """Get tasks with filters"""
        return await self.process({
            "action": "get",
            "params": filters
        })
    
    async def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Complete a task"""
        return await self.process({
            "action": "complete",
            "params": {"task_id": task_id}
        })

class ScheduleAgent(SubAgent):
    """Agent for managing schedules and calendar"""
    
    def __init__(self):
        super().__init__("ScheduleAgent")
        self.tool = MCPToolFactory.get_tool("calendar")
    
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process schedule-related requests"""
        action = task_data.get("action", "create")
        
        result = await self.tool.execute(action, **task_data.get("params", {}))
        
        return {
            "agent": self.name,
            "action": action,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def create_event(self, title: str, start_time: datetime, 
                          end_time: datetime, **kwargs) -> Dict[str, Any]:
        """Create a calendar event"""
        return await self.process({
            "action": "create",
            "params": {
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                **kwargs
            }
        })
    
    async def get_events(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get events in date range"""
        return await self.process({
            "action": "get",
            "params": {"start_date": start_date, "end_date": end_date}
        })

class NotesAgent(SubAgent):
    """Agent for managing notes"""
    
    def __init__(self):
        super().__init__("NotesAgent")
        self.tool = MCPToolFactory.get_tool("notes")
    
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process note-related requests"""
        action = task_data.get("action", "create")
        
        result = await self.tool.execute(action, **task_data.get("params", {}))
        
        return {
            "agent": self.name,
            "action": action,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def create_note(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """Create a note"""
        return await self.process({
            "action": "create",
            "params": {"title": title, "content": content, **kwargs}
        })
    
    async def get_notes(self, **filters) -> Dict[str, Any]:
        """Get notes with filters"""
        return await self.process({
            "action": "get",
            "params": filters
        })

# Sub-agent manager
class SubAgentManager:
    """Manages all sub-agents"""
    
    def __init__(self):
        self.agents = {
            "task": TaskAgent(),
            "schedule": ScheduleAgent(),
            "notes": NotesAgent()
        }
    
    def get_agent(self, agent_name: str) -> SubAgent:
        """Get a sub-agent by name"""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        return self.agents[agent_name]
    
    def list_agents(self) -> List[str]:
        """List all available agents"""
        return list(self.agents.keys())
    
    async def dispatch(self, agent_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a task to a sub-agent"""
        agent = self.get_agent(agent_name)
        return await agent.process(task_data)
