"""API Test Script - Demonstrates system functionality"""
import httpx
import asyncio
import json
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8000"

async def test_api():
    """Test all API endpoints"""
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("=" * 60)
        print("Multi-Agent Productivity Assistant - API Tests")
        print("=" * 60)
        
        # 1. Health Check
        print("\n[1] Health Check")
        response = await client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # 2. List Available Agents
        print("\n[2] List Available Agents")
        response = await client.get("/agents")
        print(f"Status: {response.status_code}")
        print(f"Agents: {response.json().get('agents')}")
        
        # 3. Create a Task
        print("\n[3] Create Task")
        task_payload = {
            "title": "Review quarterly report",
            "description": "Comprehensive review of Q1 performance",
            "priority": 1,
            "due_date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        }
        response = await client.post("/tasks", json=task_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        task_id = response.json().get("task_id", "task_1")
        
        # 4. List Tasks
        print("\n[4] List Tasks")
        response = await client.get("/tasks")
        print(f"Status: {response.status_code}")
        print(f"Task Count: {response.json().get('result', {}).get('count', 0)}")
        
        # 5. Create Schedule Event
        print("\n[5] Create Schedule Event")
        schedule_payload = {
            "title": "Q1 Review Meeting",
            "description": "Meeting to discuss quarterly performance",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=6, hours=14)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=6, hours=15)).isoformat(),
            "location": "Conference Room A"
        }
        response = await client.post("/schedules", json=schedule_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # 6. Create Note
        print("\n[6] Create Note")
        note_payload = {
            "title": "Q1 Performance Notes",
            "content": "Key achievements: Team productivity increased by 15%, Project delivery on schedule",
            "tags": ["performance", "q1", "review"]
        }
        response = await client.post("/notes", json=note_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # 7. Execute Workflow
        print("\n[7] Execute Multi-Step Workflow")
        workflow_payload = {
            "workflow_id": "project_kickoff",
            "steps": [
                {
                    "id": "task_step",
                    "agent": "task",
                    "data": {
                        "action": "create",
                        "params": {
                            "title": "Project Planning",
                            "description": "Define project scope and timeline",
                            "priority": 2
                        }
                    },
                    "depends_on": []
                },
                {
                    "id": "schedule_step",
                    "agent": "schedule",
                    "data": {
                        "action": "create",
                        "params": {
                            "title": "Project Kickoff Meeting",
                            "start_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=10)).isoformat(),
                            "end_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=11)).isoformat(),
                            "location": "Main Office"
                        }
                    },
                    "depends_on": ["task_step"]
                },
                {
                    "id": "notes_step",
                    "agent": "notes",
                    "data": {
                        "action": "create",
                        "params": {
                            "title": "Project Setup Notes",
                            "content": "Initial project setup and configuration details",
                            "tags": ["project", "setup"]
                        }
                    },
                    "depends_on": ["task_step"]
                }
            ]
        }
        response = await client.post("/workflows/execute", json=workflow_payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Workflow ID: {result.get('workflow_id')}")
        print(f"Workflow Status: {result.get('status')}")
        print(f"Steps Executed: {len(result.get('steps', []))}")
        for step in result.get('steps', []):
            print(f"  - {step['step_id']}: {step['status']}")
        
        # 8. Get Execution History
        print("\n[8] Get Execution History")
        response = await client.get("/history?limit=10")
        print(f"Status: {response.status_code}")
        history = response.json()
        print(f"Total Executions: {history.get('count', 0)}")
        print(f"Latest {min(3, history.get('count', 0))} executions:")
        for execution in history.get('executions', [])[-3:]:
            print(f"  - {execution.get('agent')}: {execution.get('status')}")
        
        # 9. Update Task
        print("\n[9] Update Task")
        update_payload = {
            "status": "in_progress",
            "priority": 2
        }
        response = await client.put(f"/tasks/{task_id}", json=update_payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # 10. Complete Task
        print("\n[10] Complete Task")
        response = await client.post(f"/tasks/{task_id}/complete")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        print("\n" + "=" * 60)
        print("API Tests Completed Successfully!")
        print("=" * 60)

if __name__ == "__main__":
    print("\nMake sure the API server is running on http://localhost:8000")
    print("Start it with: python -m uvicorn api.main:app --reload\n")
    
    try:
        asyncio.run(test_api())
    except httpx.ConnectError:
        print("Error: Could not connect to API server at http://localhost:8000")
        print("Please start the server first with: python -m uvicorn api.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")
