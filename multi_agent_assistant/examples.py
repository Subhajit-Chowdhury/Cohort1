"""Example usage of the Multi-Agent Productivity Assistant"""
import asyncio
from datetime import datetime, timedelta, timezone
from agents.coordinator import PrimaryAgentCoordinator, WorkflowStep

async def example_single_task():
    """Example: Execute a single task"""
    coordinator = PrimaryAgentCoordinator()
    
    print("\n=== Example 1: Single Task Execution ===")
    
    # Create a task
    result = await coordinator.execute_task(
        "task",
        {
            "action": "create",
            "params": {
                "title": "Review quarterly report",
                "description": "Review and approve Q1 quarterly report",
                "priority": 1,
                "due_date": datetime.now(timezone.utc) + timedelta(days=2)
            }
        }
    )
    
    print(f"Task Creation Result:")
    print(f"  Status: {result['result']['status']}")
    print(f"  Task ID: {result['result'].get('task_id', 'N/A')}")
    print(f"  Agent: {result['agent']}")

async def example_workflow():
    """Example: Execute a multi-step workflow"""
    coordinator = PrimaryAgentCoordinator()
    
    print("\n=== Example 2: Multi-Step Workflow ===")
    
    # Define workflow steps
    steps = [
        WorkflowStep(
            step_id="create_task",
            agent_name="task",
            task_data={
                "action": "create",
                "params": {
                    "title": "Project Kickoff Meeting",
                    "description": "Initial meeting for new AI project",
                    "priority": 2
                }
            },
            depends_on=[]
        ),
        WorkflowStep(
            step_id="schedule_event",
            agent_name="schedule",
            task_data={
                "action": "create",
                "params": {
                    "title": "Project Kickoff",
                    "start_time": datetime.now(timezone.utc) + timedelta(days=1, hours=10),
                    "end_time": datetime.now(timezone.utc) + timedelta(days=1, hours=11),
                    "location": "Conference Room A"
                }
            },
            depends_on=[]
        ),
        WorkflowStep(
            step_id="create_note",
            agent_name="notes",
            task_data={
                "action": "create",
                "params": {
                    "title": "Project Requirements",
                    "content": "Initial requirements for AI project coordination platform",
                    "tags": ["project", "ai", "requirements"]
                }
            },
            depends_on=["create_task"]
        )
    ]
    
    # Execute workflow
    result = await coordinator.execute_workflow("project_setup", steps)
    
    print(f"Workflow: {result['workflow_id']}")
    print(f"Status: {result['status']}")
    print(f"Steps Executed: {len(result['steps'])}")
    for step in result["steps"]:
        print(f"  - {step['step_id']}: {step['status']}")

async def example_dependent_tasks():
    """Example: Execute tasks with dependencies"""
    coordinator = PrimaryAgentCoordinator()
    
    print("\n=== Example 3: Dependent Tasks ===")
    
    steps = [
        WorkflowStep(
            step_id="create_task",
            agent_name="task",
            task_data={
                "action": "create",
                "params": {
                    "title": "Write proposal",
                    "priority": 1,
                    "due_date": datetime.now(timezone.utc) + timedelta(days=3)
                }
            },
            depends_on=[]
        ),
        WorkflowStep(
            step_id="create_event",
            agent_name="schedule",
            task_data={
                "action": "create",
                "params": {
                    "title": "Proposal Review",
                    "start_time": datetime.now(timezone.utc) + timedelta(days=4, hours=14),
                    "end_time": datetime.now(timezone.utc) + timedelta(days=4, hours=15),
                    "location": "Virtual"
                }
            },
            depends_on=["create_task"]
        )
    ]
    
    result = await coordinator.execute_workflow("dependent_workflow", steps)
    
    print(f"Workflow: {result['workflow_id']}")
    print(f"Status: {result['status']}")
    for step in result["steps"]:
        print(f"  {step['step_id']}: {step['status']}")

async def example_execution_history():
    """Example: View execution history"""
    coordinator = PrimaryAgentCoordinator()
    
    print("\n=== Example 4: Execution History ===")
    
    # Execute some tasks
    for i in range(3):
        await coordinator.execute_task(
            "task",
            {
                "action": "create",
                "params": {
                    "title": f"Task {i+1}",
                    "priority": i
                }
            }
        )
    
    # Get history
    history = coordinator.get_execution_history(limit=10)
    
    print(f"Total Executions: {len(history)}")
    for execution in history[-3:]:
        print(f"  Agent: {execution['agent']}, Status: {execution['status']}")

async def example_list_agents():
    """Example: List available agents"""
    coordinator = PrimaryAgentCoordinator()
    
    print("\n=== Example 5: Available Agents ===")
    
    agents = coordinator.list_available_agents()
    print(f"Available Agents: {', '.join(agents)}")

async def main():
    """Run all examples"""
    print("=" * 60)
    print("Multi-Agent Productivity Assistant - Usage Examples")
    print("=" * 60)
    
    await example_single_task()
    await example_workflow()
    await example_dependent_tasks()
    await example_execution_history()
    await example_list_agents()
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
