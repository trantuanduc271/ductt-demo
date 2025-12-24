# Awareness Agent - Quick Start Guide

## Prerequisites

1. **PostgreSQL Database** - Already set up via Docker
2. **Python Dependencies** - Install required packages

## Step 1: Start the Database

```bash
cd D:\Bestarion\test\ductt-demo\agent\awareness_agent
docker-compose up -d
```

Verify it's running:
```bash
docker ps | findstr security_training_db
```

## Step 2: Install Dependencies

```bash
cd D:\Bestarion\test
.\.venv\Scripts\pip install -r ductt-demo\agent\awareness_agent\requirements.txt
```

## Step 3: Start Library Agent (Port 9999)

```bash
cd D:\Bestarion\test\ductt-demo\agent\library_agent
..\..\..\.venv\Scripts\python -m library_agent
```

Keep this terminal open - the agent will run on port 9999.

## Step 4: Start Awareness Agent (Port 9998)

Open a **new terminal**:

```bash
cd D:\Bestarion\test\ductt-demo\agent\awareness_agent
..\..\..\.venv\Scripts\python -m awareness_agent
```

Keep this terminal open - the agent will run on port 9998.

## Step 5: Import User Awareness Status Data

### Option A: Via Agent (Recommended)

Once the Awareness Agent is running, you can ask it:

```
"Import user awareness status from user_awareness_status.json"
```

Or via the root agent:
```
"Ask the security training orchestrator to import user awareness status from user_awareness_status.json"
```

### Option B: Direct Python Script

```bash
cd D:\Bestarion\test\ductt-demo\agent\awareness_agent
..\..\..\.venv\Scripts\python -c "from db_utils import import_user_awareness_from_json; print(import_user_awareness_from_json('user_awareness_status.json'))"
```

## Step 6: Start Root Agent (Optional - for orchestration)

Open a **third terminal**:

```bash
cd D:\Bestarion\test\ductt-demo\agent\devops_root
..\..\..\.venv\Scripts\python -m devops_root
```

The root agent is already configured to connect to the Awareness Agent on port 9998.

## Step 7: Test the System

### Via Root Agent:
```
"Ask the security training orchestrator to load the current user awareness status and identify all overdue or missing training assignments"
```

### Direct to Awareness Agent:
```
"Load the current user awareness status and identify all overdue or missing training assignments. Generate the assignment plan and request approval."
```

## Connection Details

- **Database**: `localhost:5433` (user: `postgres`, password: `postgres`, db: `security_training`)
- **Library Agent**: `http://localhost:9999`
- **Awareness Agent**: `http://localhost:9998`
- **Root Agent**: Already configured to use Awareness Agent

## Importing New Data

### Update user_awareness_status.json

Edit `user_awareness_status.json` with new user data, then:

1. **Via Agent**: "Import user awareness status from user_awareness_status.json"
2. **Or Direct**: Use the Python script in Option B above

### Data Format

The JSON file should contain an array of user objects:
```json
[
  {
    "user_id": "alice",
    "name": "Alice",
    "department": "HR",
    "region": "EU",
    "overall_status": "NON_COMPLIANT",
    "last_evaluated": "2025-12-19T00:00:00",
    "training_status": [
      {
        "module_id": "TRN-001",
        "status": "OVERDUE",
        "last_completed": "2024-10-01",
        "days_overdue": 79
      }
    ]
  }
]
```

## Troubleshooting

- **Port conflicts**: Make sure ports 9998, 9999, and 5433 are free
- **Database connection**: Verify `docker ps` shows `security_training_db` running
- **Agent not responding**: Check the terminal output for errors

