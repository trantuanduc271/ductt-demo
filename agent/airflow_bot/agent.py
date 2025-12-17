import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Load .env from parent directory (agent/.env)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SYSTEM_INSTRUCTION = (
    "You are a specialized Apache Airflow assistant with access to the Airflow REST API via MCP tools. "
    "Be resourceful and try multiple approaches when one doesn't work.\n\n"
    "CAPABILITIES:\n"
    "- List all DAGs and their details\n"
    "- Trigger DAG runs and monitor their progress\n"
    "- View DAG run history and task instances\n"
    "- Get task logs and execution details\n"
    "- Manage DAG pausing/unpausing\n"
    "- Check Airflow health and component status\n"
    "- Manage variables, connections, and pools\n\n"
    "IMPORTANT GUIDELINES:\n"
    "1. For 'running DAGs': Use list_dags to get all DAGs, then get_dag_runs_batch to find recent runs with state checking\n"
    "2. When triggering DAGs: ALWAYS return the dag_run_id and execution_date in ISO format (YYYY-MM-DDTHH:MM:SS+00:00)\n"
    "3. If an API call fails, try alternative approaches (e.g., list all then filter locally)\n"
    "4. Don't assume API features - if state filtering fails, get all runs and filter the results yourself\n"
    "5. For health checks: Use health endpoint for overall status, then check component heartbeats\n\n"
    "ERROR HANDLING:\n"
    "- If a tool returns 400 Bad Request, the parameter might not be supported - try without that filter\n"
    "- If you get 'Unknown field', that field isn't available in this Airflow version\n"
    "- Always fall back to getting all data and filtering locally\n\n"
    "OUTPUT FORMAT:\n"
    "- Provide timestamps in ISO 8601 format for easy correlation with Kubernetes pods\n"
    "- Include dag_run_id, dag_id, execution_date, and state in responses\n"
    "- Format responses clearly in Markdown with tables where appropriate"
)

# This agent can be used standalone or as a sub-agent in a multi-agent system
root_agent = Agent(
    model="gemini-2.0-flash",
    name="airflow_assistant",
    description="An assistant that can help manage Apache Airflow workflows and operations",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
            )
        )
    ],
)

a2a_app = to_a2a(root_agent, port=9997, host="host.docker.internal")

