"""Unit tests for the Multi-Agent Productivity Assistant"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from agents.coordinator import PrimaryAgentCoordinator, WorkflowStep
from agents.sub_agents import TaskAgent, ScheduleAgent, NotesAgent, SubAgentManager
from mcp_tools.tools import MCPToolFactory, CalendarTool, TaskManagerTool, NotesTool

# Test fixtures
@pytest.fixture
def coordinator():
    """Create a coordinator instance"""
    return PrimaryAgentCoordinator()

@pytest.fixture
def task_agent():
    """Create a task agent instance"""
    return TaskAgent()

@pytest.fixture
def schedule_agent():
    """Create a schedule agent instance"""
    return ScheduleAgent()

@pytest.fixture
def notes_agent():
    """Create a notes agent instance"""
    return NotesAgent()

# MCP Tools Tests
@pytest.mark.asyncio
async def test_calendar_tool_create_event():
    """Test calendar tool event creation"""
    tool = CalendarTool()
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)
    
    result = await tool.create_event(
        title="Test Event",
        start_time=start,
        end_time=end,
        location="Test Location"
    )
    
    assert result["status"] == "success"
    assert result["title"] == "Test Event"
    assert "event_id" in result

@pytest.mark.asyncio
async def test_task_manager_tool_create_task():
    """Test task manager tool"""
    tool = TaskManagerTool()
    
    result = await tool.create_task(
        title="Test Task",
        description="Test Description",
        priority=1
    )
    
    assert result["status"] == "success"
    assert result["title"] == "Test Task"
    assert "task_id" in result

@pytest.mark.asyncio
async def test_notes_tool_create_note():
    """Test notes tool"""
    tool = NotesTool()
    
    result = await tool.create_note(
        title="Test Note",
        content="Test Content",
        tags=["test"]
    )
    
    assert result["status"] == "success"
    assert result["title"] == "Test Note"
    assert "note_id" in result

# Sub-Agent Tests
@pytest.mark.asyncio
async def test_task_agent_create_task(task_agent):
    """Test task agent creation"""
    result = await task_agent.create_task(
        title="Test Task",
        description="Test Description"
    )
    
    assert result["agent"] == "TaskAgent"
    assert result["action"] == "create"
    assert result["result"]["status"] == "success"

@pytest.mark.asyncio
async def test_schedule_agent_create_event(schedule_agent):
    """Test schedule agent"""
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)
    
    result = await schedule_agent.create_event(
        title="Test Event",
        start_time=start,
        end_time=end
    )
    
    assert result["agent"] == "ScheduleAgent"
    assert result["action"] == "create"
    assert result["result"]["status"] == "success"

@pytest.mark.asyncio
async def test_notes_agent_create_note(notes_agent):
    """Test notes agent"""
    result = await notes_agent.create_note(
        title="Test Note",
        content="Test Content"
    )
    
    assert result["agent"] == "NotesAgent"
    assert result["action"] == "create"
    assert result["result"]["status"] == "success"

# Coordinator Tests
@pytest.mark.asyncio
async def test_coordinator_execute_single_task(coordinator):
    """Test coordinator single task execution"""
    result = await coordinator.execute_task(
        "task",
        {
            "action": "create",
            "params": {
                "title": "Test Task"
            }
        }
    )
    
    assert result["agent"] == "TaskAgent"
    assert result["action"] == "create"
    assert result["result"]["status"] == "success"

@pytest.mark.asyncio
async def test_coordinator_workflow_execution(coordinator):
    """Test coordinator workflow execution"""
    steps = [
        WorkflowStep(
            step_id="step1",
            agent_name="task",
            task_data={"action": "create", "params": {"title": "Task 1"}},
            depends_on=[]
        ),
        WorkflowStep(
            step_id="step2",
            agent_name="notes",
            task_data={"action": "create", "params": {"title": "Note 1", "content": "Content"}},
            depends_on=[]
        )
    ]
    
    result = await coordinator.execute_workflow("test_workflow", steps)
    
    assert result["workflow_id"] == "test_workflow"
    assert result["status"] == "completed"
    assert len(result["steps"]) == 2

@pytest.mark.asyncio
async def test_coordinator_workflow_with_dependencies(coordinator):
    """Test workflow with dependencies"""
    steps = [
        WorkflowStep(
            step_id="step1",
            agent_name="task",
            task_data={"action": "create", "params": {"title": "Task 1"}},
            depends_on=[]
        ),
        WorkflowStep(
            step_id="step2",
            agent_name="task",
            task_data={"action": "create", "params": {"title": "Task 2"}},
            depends_on=["step1"]
        )
    ]
    
    result = await coordinator.execute_workflow("test_workflow_deps", steps)
    
    assert result["status"] == "completed"
    assert len(result["steps"]) == 2
    # Verify step2 depends on step1
    assert result["steps"][1]["status"] == "completed"

# Sub-Agent Manager Tests
def test_subagent_manager_list_agents():
    """Test listing all agents"""
    manager = SubAgentManager()
    agents = manager.list_agents()
    
    assert "task" in agents
    assert "schedule" in agents
    assert "notes" in agents

def test_subagent_manager_get_agent():
    """Test getting an agent"""
    manager = SubAgentManager()
    agent = manager.get_agent("task")
    
    assert agent is not None
    assert agent.name == "TaskAgent"

# MCP Tool Factory Tests
def test_mcp_tool_factory_get_tool():
    """Test getting tools from factory"""
    calendar_tool = MCPToolFactory.get_tool("calendar")
    assert isinstance(calendar_tool, CalendarTool)
    
    task_tool = MCPToolFactory.get_tool("task_manager")
    assert isinstance(task_tool, TaskManagerTool)
    
    notes_tool = MCPToolFactory.get_tool("notes")
    assert isinstance(notes_tool, NotesTool)

def test_mcp_tool_factory_list_tools():
    """Test listing all tools"""
    tools = MCPToolFactory.list_tools()
    
    assert "calendar" in tools
    assert "task_manager" in tools
    assert "notes" in tools

# Helper function to run async tests
def run_async_test(coro):
    """Run async test"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
