# Quick Setup Guide

## Prerequisites Installation

### 1. Install uv (Python Package Manager)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal or open a new one.

### 2. Get Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the generated API key

### 3. Configure Environment

The `.env` file in the parent directory (`agent/.env`) should contain:

```env
GOOGLE_API_KEY=your_api_key_here
AIRFLOW_URL=https://airflow.ducttdevops.com
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
MCP_SERVER_URL=http://localhost:8080/mcp
```

## Running the Airflow Bot

### Step 1: Start the MCP Server

**Terminal 1 - Windows PowerShell:**
```powershell
cd mcp\mcp-server-apache-airflow
$env:AIRFLOW_BASE_URL="https://airflow.ducttdevops.com"
$env:AIRFLOW_USERNAME="admin"
$env:AIRFLOW_PASSWORD="admin"
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
```

**Terminal 1 - Linux/macOS:**
```bash
cd mcp/mcp-server-apache-airflow
export AIRFLOW_BASE_URL="https://airflow.ducttdevops.com"
export AIRFLOW_USERNAME="admin"
export AIRFLOW_PASSWORD="admin"
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
```

### Step 2: Start the ADK Web UI

**Terminal 2:**
```powershell
cd agent\airflow_bot
adk web
```

This will open your browser automatically with the ADK web interface!

## Using the Agent

1. Once the ADK web UI opens in your browser, you'll see a chat interface
2. Type your Airflow-related questions in natural language
3. The agent will use the MCP tools to interact with your Airflow instance

### Example Queries

Try these queries:

- "List all DAGs in my Airflow instance"
- "What is the health status of my Airflow?"
- "Show me all paused DAGs"
- "Trigger a DAG run for ml_pipeline_dag"
- "Get recent failed task instances"
- "List all Airflow variables"

## Troubleshooting

### "Connection refused" errors
- Ensure MCP server is running on port 8080
- Check that Airflow instance is accessible
- Verify credentials in .env file

### "API Key invalid" errors
- Verify your Google API key is correct
- Check that the key is active in Google AI Studio

### "Module not found" errors
- Run `uv sync` to install dependencies
- Ensure you're in the correct directory

### MCP Server can't connect to Airflow
- Verify Airflow URL is correct and accessible
- Check that REST API is enabled in Airflow
- Confirm username/password have appropriate permissions

## Project Structure

```
airflow_bot/
├── airflow_bot/           # Main package
│   ├── __init__.py       # Package initialization
│   └── agent.py          # ADK agent with MCP integration
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore rules
├── pyproject.toml       # Dependencies
├── README.md            # Full documentation
└── SETUP.md             # This file
```

## Next Steps

1. **Customize the Agent**: Modify [airflow_bot/agent.py](airflow_bot/agent.py) to adjust the system instruction or model
2. **Explore Tools**: Use the ADK web UI to see what MCP tools are available
3. **Deploy**: Check the ADK documentation for production deployment options

## Getting Help

- Review the full [README.md](README.md) for detailed information
- Check [MCP Server documentation](../../mcp/mcp-server-apache-airflow/README.md)
- Visit [ADK documentation](https://github.com/google/adk-python)

### 1. Install uv (Python Package Manager)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal or open a new one.

### 2. Get Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the generated API key

### 3. Configure Environment

The `.env` file in the parent directory (`agent/.env`) should contain:

```env
GOOGLE_API_KEY=your_api_key_here
AIRFLOW_URL=https://airflow.ducttdevops.com
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
MCP_SERVER_URL=http://localhost:8080/mcp
```

## Running the Airflow Bot

### Option 1: Using the Startup Script (Recommended)

**Windows:**
```powershell
cd agent/airflow_bot
.\start.ps1
```

This will open two PowerShell windows:
- One for the MCP Server (port 8080)
- One for the A2A Server (port 10000)

**Linux/macOS:**
```bash
cd agent/airflow_bot
chmod +x start.sh
./start.sh
```

Press Ctrl+C to stop all servers.

### Option 2: Manual Startup

**Terminal 1 - Start MCP Server:**
```bash
cd mcp/mcp-server-apache-airflow

# Set environment variables
export AIRFLOW_BASE_URL="https://airflow.ducttdevops.com"
export AIRFLOW_USERNAME="admin"
export AIRFLOW_PASSWORD="admin"

# Start MCP server
uv run python -m src.main --transport http --mcp-host 0.0.0.0 --mcp-port 8080
```

**Terminal 2 - Start A2A Server:**
```bash
cd agent/airflow_bot
uv run uvicorn airflow_bot.agent:a2a_app --host localhost --port 10000
```

**Terminal 3 - Run Test Client:**
```bash
cd agent/airflow_bot
uv run python airflow_bot/test_client.py
```

## Testing the Bot

Once both servers are running, you can test the agent:

```bash
cd agent/airflow_bot
uv run python airflow_bot/test_client.py
```

The test client will:
1. Connect to the A2A server
2. Send sample queries about Airflow
3. Display the responses

## Example Queries

Try these queries with your Airflow bot:

- "List all DAGs in my Airflow instance"
- "What is the health status of my Airflow?"
- "Show me all paused DAGs"
- "Trigger a DAG run for ml_pipeline_dag"
- "Get recent failed task instances"
- "List all Airflow variables"

## Troubleshooting

### "Connection refused" errors
- Ensure MCP server is running on port 8080
- Check that Airflow instance is accessible
- Verify credentials in .env file

### "API Key invalid" errors
- Verify your Google API key is correct
- Check that the key is active in Google AI Studio

### "Module not found" errors
- Run `uv sync` to install dependencies
- Ensure you're in the correct directory

### MCP Server can't connect to Airflow
- Verify Airflow URL is correct and accessible
- Check that REST API is enabled in Airflow
- Confirm username/password have appropriate permissions

## Project Structure

```
airflow_bot/
├── airflow_bot/           # Main package
│   ├── __init__.py       # Package initialization
│   ├── agent.py          # ADK agent with MCP integration
│   └── test_client.py    # A2A test client
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore rules
├── pyproject.toml       # Dependencies
├── README.md            # Full documentation
├── SETUP.md             # This file
├── start.ps1            # Windows startup script
└── start.sh             # Linux/macOS startup script
```

## Next Steps

1. **Customize the Agent**: Modify [airflow_bot/agent.py](airflow_bot/agent.py) to adjust the system instruction or model
2. **Add More Tests**: Extend [airflow_bot/test_client.py](airflow_bot/test_client.py) with your own queries
3. **Deploy**: Follow the README for production deployment options

## Getting Help

- Review the full [README.md](README.md) for detailed information
- Check [MCP Server documentation](../../mcp/mcp-server-apache-airflow/README.md)
- Visit [ADK documentation](https://github.com/google/adk-python)
