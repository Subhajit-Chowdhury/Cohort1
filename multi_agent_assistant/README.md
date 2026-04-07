# Multi-Agent Productivity Assistant

A sophisticated multi-agent AI system that coordinates multiple agents to help users manage tasks, schedules, and information through an integrated API-based platform.

## Overview

This system demonstrates:
- **Primary Agent Coordination**: Central coordinator managing multiple specialized sub-agents
- **Database Integration**: Structured data persistence with SQLAlchemy ORM
- **MCP Tool Integration**: Calendar, task manager, and notes tools
- **Multi-Step Workflows**: Dependency-aware workflow execution
- **RESTful API**: FastAPI-based deployment
- **Agent Specialization**: Task, Schedule, and Notes agents

## Architecture

```
Multi-Agent Productivity Assistant
├── Primary Agent Coordinator (orchestration)
│   └── Sub-Agents
│       ├── Task Agent
│       ├── Schedule Agent
│       └── Notes Agent
├── MCP Tools
│   ├── Calendar Tool
│   ├── Task Manager Tool
│   └── Notes Tool
├── Database Layer
│   └── SQLAlchemy Models
└── API Layer
    └── FastAPI Endpoints
```

## Features

### Core Features
1. **Task Management**: Create, update, complete tasks with priorities and deadlines
2. **Schedule Management**: Calendar integration with recurring event support
3. **Notes Management**: Create and organize notes with tags and search
4. **Multi-Step Workflows**: Execute coordinated tasks across agents
5. **Dependency Handling**: Resolve dependencies between workflow steps
6. **Execution History**: Track all agent executions

### API Capabilities
- REST endpoints for all operations
- Workflow execution and scheduling
- Multi-agent coordination
- Execution history tracking
- Health monitoring

## Quick Start

### 1. Installation

```bash
cd "h:\Win 11\My Work\My Projects\H2S\Cohort1\multi_agent_assistant"
pip install -r requirements.txt
```

### 2. Starting the API Server

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Interactive Documentation

Access Swagger UI: `http://localhost:8000/docs`
Access ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Tasks
```
POST   /tasks               - Create a task
GET    /tasks               - List tasks
PUT    /tasks/{task_id}     - Update a task
POST   /tasks/{task_id}/complete - Complete a task
```

### Schedules
```
POST   /schedules           - Create a schedule/event
GET    /schedules           - List schedules
```

### Notes
```
POST   /notes               - Create a note
GET    /notes               - List notes
```

### Workflows
```
POST   /workflows/execute   - Execute a workflow immediately
POST   /workflows/schedule  - Schedule a workflow
GET    /workflows/{id}      - Get workflow status
```

### Utilities
```
GET    /                    - Welcome endpoint
GET    /health              - Health check
GET    /agents              - List available agents
GET    /history             - View execution history
```

## Usage Examples

### 1. Create a Task

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review report",
    "description": "Review quarterly report",
    "priority": 1,
    "due_date": "2026-04-15T10:00:00"
  }'
```

### 2. Create a Schedule Event

```bash
curl -X POST "http://localhost:8000/schedules" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "start_time": "2026-04-08T14:00:00",
    "end_time": "2026-04-08T15:00:00",
    "location": "Conference Room A"
  }'
```

### 3. Execute a Multi-Step Workflow

```bash
curl -X POST "http://localhost:8000/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "project_setup",
    "steps": [
      {
        "id": "task1",
        "agent": "task",
        "data": {
          "action": "create",
          "params": {
            "title": "Project Setup",
            "priority": 1
          }
        },
        "depends_on": []
      },
      {
        "id": "event1",
        "agent": "schedule",
        "data": {
          "action": "create",
          "params": {
            "title": "Project Kickoff",
            "start_time": "2026-04-10T10:00:00",
            "end_time": "2026-04-10T11:00:00"
          }
        },
        "depends_on": ["task1"]
      }
    ]
  }'
```

### 4. Run Python Examples

```bash
python examples.py
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/test_main.py::test_coordinator_execute_single_task -v
```

## Project Structure

```
multi_agent_assistant/
├── agents/
│   ├── __init__.py
│   ├── coordinator.py        # Primary coordinator
│   └── sub_agents.py         # Task, Schedule, Notes agents
├── db/
│   ├── __init__.py
│   └── models.py             # Database models
├── mcp_tools/
│   ├── __init__.py
│   └── tools.py              # Tool integrations
├── api/
│   └── main.py               # FastAPI application
├── tests/
│   └── test_main.py          # Unit tests
├── config.py                 # Configuration
├── examples.py               # Usage examples
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Database Schema

### Users
- id (primary key)
- email (unique)
- name
- created_at

### Tasks
- id (primary key)
- user_id (foreign key)
- title (indexed)
- description
- status (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- priority
- due_date
- timestamps

### Schedules
- id (primary key)
- user_id (foreign key)
- title (indexed)
- description
- start_time, end_time
- location
- recurrence support

### Notes
- id (primary key)
- user_id (foreign key)
- title (indexed)
- content
- tags
- timestamps

### Workflows
- id (primary key)
- user_id (foreign key)
- name (indexed)
- status
- timestamps

## Workflow Execution

### Dependency Resolution
```python
# Step 2 depends on Step 1
{
  "step_id": "step2",
  "agent": "schedule",
  "data": {...},
  "depends_on": ["step1"]
}
```

### Placeholder Resolution
```python
# Use results from previous steps
"title": "${step1.task_id}:follow-up"
```

## Configuration

### Environment Variables

```
DATABASE_URL=sqlite:///./productivity_assistant.db
PORT=8000
LOG_LEVEL=INFO
```

## Error Handling

All errors return JSON with:
```json
{
  "error": "Error message",
  "timestamp": "2026-04-07T10:30:00.000000"
}
```

## Performance Considerations

- **Workflow Timeout**: 300 seconds (5 minutes)
- **Tool Timeouts**: 30 seconds each
- **Max Workflow Steps**: 100 per workflow
- **Database**: SQLite (production: PostgreSQL recommended)

## Future Enhancements

1. **Integration with Real Tools**
   - Google Calendar API
   - Microsoft Teams integration
   - Slack notifications

2. **Advanced Features**
   - Machine learning for task prioritization
   - Natural language processing for task creation
   - Collaboration and sharing

3. **Scaling**
   - Distributed workflow execution
   - Message queue integration
   - Multi-machine deployment

4. **Monitoring**
   - Metrics and analytics
   - Performance monitoring
   - Audit logging

## License

MIT License

## Support

For issues, questions, or contributions, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: April 7, 2026
