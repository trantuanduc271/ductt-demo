# 🌬️ Airflow Bot (ADK + MCP)

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg)](https://github.com/google/adk-python)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A specialized agent for managing Apache Airflow using the Agent Development Kit (ADK) and Model Context Protocol (MCP). This agent allows you to interact with your Airflow instance through natural language using the ADK Web UI.

## Overview

The Airflow Bot demonstrates how ADK and MCP work together to create a powerful AI agent for Apache Airflow management, similar to the kubernetes_bot.

### <img height="20" width="20" src="https://modelcontextprotocol.io/favicon.ico" alt="MCP Logo" /> Model Context Protocol (MCP)

The bot connects to the [mcp-server-apache-airflow](../../mcp/mcp-server-apache-airflow) MCP server, which exposes comprehensive Airflow REST API operations as standardized tools:

- **DAG Management**: List, pause, unpause, update, and delete DAGs
- **DAG Runs**: Create, monitor, and manage DAG runs
- **Task Operations**: View task instances, logs, and manage their state
- **Variables & Connections**: Manage Airflow variables and connections
- **Monitoring**: Check health status and view metrics
- **Datasets & XComs**: Work with datasets and cross-communication

### <img height="20" width="20" src="https://github.com/google/adk-python/raw/main/docs/assets/adk-logo.png" alt="ADK Logo" /> Agent Development Kit (ADK)

ADK orchestrates the conversation and tool invocations through a simple web interface:
- Natural language understanding of Airflow-related queries
- Intelligent routing to appropriate MCP tools
- Interactive web UI for chatting with the agent

## Getting Started

### Prerequisites

- Python 3.10+
- Apache Airflow instance (accessible via REST API)
- Google API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Setup

1. The `.env` file in the parent directory should contain:

```dotenv
GOOGLE_API_KEY=your_google_api_key_here
AIRFLOW_URL=https://your-airflow-instance.com
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
MCP_SERVER_URL=http://localhost:8080/mcp
```

## Running the Bot

### Step 1: Start the Airflow MCP Server

In a terminal, start the MCP server:

**Windows PowerShell:**
```powershell
cd ..\..\mcp\mcp-server-apache-airflow
$env:AIRFLOW_BASE_URL="https://airflow.ducttdevops.com"
$env:AIRFLOW_USERNAME="admin"
$env:AIRFLOW_PASSWORD="admin"
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
```

**Linux/macOS:**
```bash
cd ../../mcp/mcp-server-apache-airflow
export AIRFLOW_BASE_URL="https://airflow.ducttdevops.com"
export AIRFLOW_USERNAME="admin"
export AIRFLOW_PASSWORD="admin"
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
```

### Step 2: Start the ADK Web UI

In a separate terminal:

**Windows PowerShell:**
```powershell
cd agent\airflow_bot
adk web
```

**Linux/macOS:**
```bash
cd agent/airflow_bot
adk web
```

This will open a web browser where you can chat with the Airflow agent!

## Example Interactions

Once the agent is running in the ADK web UI, you can interact with it using natural language:

- "List all DAGs in my Airflow instance"
- "What is the health status of my Airflow?"
- "Show me all paused DAGs"
- "Trigger a DAG run for the ml_pipeline_dag"
- "What are the recent failed task instances?"
- "Get the logs for task X in DAG Y"
- "List all Airflow variables"
- "Create a new Airflow variable named 'api_key'"

## Architecture

```
┌──────────────┐
│   User       │
│  (ADK Web)   │
└──────┬───────┘
       │ Natural Language Query
       ▼
┌──────────────────┐
│  Airflow Bot     │
│  (ADK Agent)     │
└──────┬───────────┘
       │ MCP Protocol
       ▼
┌────────────────────┐
│  Airflow MCP       │
│  Server            │
└──────┬─────────────┘
       │ REST API
       ▼
┌────────────────────┐
│  Apache Airflow    │
│  Instance          │
└────────────────────┘
```

## Project Structure

```
airflow_bot/
├── airflow_bot/
│   ├── __init__.py       # Package initialization
│   └── agent.py          # Main agent with MCP integration
├── .env.example          # Example environment variables
├── .gitignore
├── pyproject.toml        # Project dependencies
└── README.md             # This file
```

## Troubleshooting

### MCP Server Connection Issues

If you get connection errors:
1. Ensure the MCP server is running on port 8080
2. Verify `MCP_SERVER_URL` in `.env` is correct
3. Check Airflow credentials in the MCP server

### Airflow API Issues

If the agent can't access Airflow:
1. Verify your Airflow instance is accessible
2. Check that the REST API is enabled
3. Confirm credentials have appropriate permissions

### ADK Web Issues

If `adk web` fails:
1. Ensure all dependencies are installed: `uv sync`
2. Check that your Google API key is valid
3. Verify Python version is 3.10+

## License

Apache License 2.0

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg)](https://github.com/google/adk-python)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A specialized agent for managing Apache Airflow using the Agent Development Kit (ADK), Agent2Agent (A2A) protocol, and Model Context Protocol (MCP). This agent allows you to interact with your Airflow instance through natural language.

## Overview

The Airflow Bot demonstrates how A2A, ADK, and MCP work together to create a powerful AI agent for Apache Airflow management. It uses:

### <img height="20" width="20" src="https://modelcontextprotocol.io/favicon.ico" alt="MCP Logo" /> Model Context Protocol (MCP)

The bot connects to the [mcp-server-apache-airflow](../../mcp/mcp-server-apache-airflow) MCP server, which exposes comprehensive Airflow REST API operations as standardized tools. This includes:

- **DAG Management**: List, pause, unpause, update, and delete DAGs
- **DAG Runs**: Create, monitor, and manage DAG runs
- **Task Operations**: View task instances, logs, and manage their state
- **Variables & Connections**: Manage Airflow variables and connections
- **Monitoring**: Check health status and view metrics
- **Datasets & XComs**: Work with datasets and cross-communication

### <img height="20" width="20" src="https://github.com/google/adk-python/raw/main/docs/assets/adk-logo.png" alt="ADK Logo" /> Agent Development Kit (ADK)

ADK (v1.0.0+) orchestrates the conversation and tool invocations. It handles:
- Natural language understanding of Airflow-related queries
- Intelligent routing to appropriate MCP tools
- Context management for multi-turn conversations

### <img height="20" width="20" src="https://a2aproject.github.io/A2A/v0.2.5/assets/a2a-logo-white.svg" alt="A2A Logo" /> Agent2Agent (A2A)

The A2A protocol makes the agent interoperable with other AI agents, enabling:
- Standardized agent-to-agent communication
- Integration with various AI systems
- Task delegation and orchestration

## Getting Started

### Prerequisites

- Python 3.10+
- Apache Airflow instance (accessible via REST API)
- Access to the Airflow MCP server

### Installation

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation) (used to manage dependencies):

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> [!NOTE]
> You may need to restart or open a new terminal after installing `uv`.

2. Configure environment variables:

The `.env` file should already be present in the parent directory with:

```dotenv
GOOGLE_API_KEY=your_google_api_key_here
AIRFLOW_URL=https://your-airflow-instance.com
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
MCP_SERVER_URL=http://localhost:8080/mcp
```

> [!TIP]
> Get an API Key from Google AI Studio: https://aistudio.google.com/apikey

## Local Deployment

### 1. Start the Airflow MCP Server

In a terminal, navigate to the MCP server directory and start it:

```bash
cd ../../mcp/mcp-server-apache-airflow

# Install dependencies if not already installed
uv sync

# Set environment variables for Airflow connection
export AIRFLOW_BASE_URL="https://airflow.ducttdevops.com"
export AIRFLOW_USERNAME="admin"
export AIRFLOW_PASSWORD="admin"

# Start the MCP server (runs on port 8080 by default)
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
```

For Windows PowerShell:
```powershell
cd ..\..\mcp\mcp-server-apache-airflow
$env:AIRFLOW_BASE_URL="https://airflow.ducttdevops.com"
$env:AIRFLOW_USERNAME="admin"
$env:AIRFLOW_PASSWORD="admin"
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
```

### 2. Start the A2A Server (Airflow Bot)

In a separate terminal, start the A2A Server (runs on port 10000):

```bash
cd agent/airflow_bot
uv run uvicorn airflow_bot.agent:a2a_app --host localhost --port 10000
```

### 3. Test the Agent

In a separate terminal, run the test client:

```bash
cd agent/airflow_bot
uv run python airflow_bot/test_client.py
```

## Example Interactions

Once the agent is running, you can interact with it using natural language:

- "List all DAGs in my Airflow instance"
- "What is the health status of my Airflow?"
- "Show me all paused DAGs"
- "Trigger a DAG run for the ml_pipeline_dag"
- "What are the recent failed task instances?"
- "Get the logs for task X in DAG Y"
- "List all Airflow variables"
- "Create a new Airflow variable named 'api_key'"

## Architecture

```
┌──────────────┐
│   User       │
└──────┬───────┘
       │ Natural Language Query
       ▼
┌──────────────────┐
│  Airflow Bot     │
│  (ADK Agent)     │
└──────┬───────────┘
       │ A2A Protocol
       ▼
┌──────────────────┐
│  MCP Toolset     │
└──────┬───────────┘
       │ MCP Protocol
       ▼
┌────────────────────┐
│  Airflow MCP       │
│  Server            │
└──────┬─────────────┘
       │ REST API
       ▼
┌────────────────────┐
│  Apache Airflow    │
│  Instance          │
└────────────────────┘
```

## Project Structure

```
airflow_bot/
├── airflow_bot/
│   ├── __init__.py       # Package initialization
│   ├── agent.py          # Main agent with MCP integration
│   └── test_client.py    # A2A test client
├── pyproject.toml        # Project dependencies
└── README.md             # This file
```

## Troubleshooting

### MCP Server Connection Issues

If you get connection errors, ensure:
1. The MCP server is running on the correct port (8080 by default)
2. The `MCP_SERVER_URL` in `.env` matches the server location
3. The Airflow credentials in the MCP server are correct

### Airflow API Issues

If the agent can't access Airflow:
1. Verify your Airflow instance is accessible
2. Check that the REST API is enabled in your Airflow configuration
3. Confirm the credentials have appropriate permissions

### Agent Initialization Errors

If the agent fails to start:
1. Ensure all dependencies are installed: `uv sync`
2. Check that your Google API key is valid
3. Verify Python version is 3.10+

## Contributing

Contributions are welcome! Feel free to:
- Report issues
- Suggest new features
- Submit pull requests

## License

Apache License 2.0
