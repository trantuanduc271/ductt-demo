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
    "You are a Kubernetes cluster management assistant with direct access to a Kubernetes cluster via MCP tools. "
    "You have all necessary credentials and configuration already loaded. "
    "Use your tools confidently to answer user questions. You can help with:\n"
    "- Listing and managing namespaces, nodes, pods, deployments, services, and other Kubernetes resources\n"
    "- Viewing pod logs and events\n"
    "- Checking resource status and details\n"
    "- Creating, updating, and deleting Kubernetes resources\n"
    "- Executing commands in pods\n"
    "- Managing Helm releases\n\n"
    "IMPORTANT for finding pods related to Airflow DAG runs:\n"
    "- When asked to find a pod for a specific DAG run, be PROACTIVE:\n"
    "  1. List pods in the namespace (e.g., airflow-3) and filter by:\n"
    "     - Creation timestamp close to the DAG run time (within 1-2 minutes)\n"
    "     - Pod name containing the DAG name or task name\n"
    "     - Labels or annotations containing dag_id, task_id, run_id\n"
    "  2. If multiple pods match, pick the most recent one or list the top candidates\n"
    "  3. Then immediately get the pod logs and events for that pod\n"
    "- DO NOT ask for more information if you have the namespace and DAG run time - just proceed\n"
    "- Airflow pods typically have labels like 'dag_id=<dag_name>'\n\n"
    "Always provide clear, well-formatted responses in Markdown. "
    "When showing resource details, organize information logically with headers and tables where appropriate."
)

# This agent can be used standalone or as a sub-agent in a multi-agent system
root_agent = Agent(
    model="gemini-2.0-flash",
    name="kubernetes_assistant",
    description="An assistant that can help you with your Kubernetes cluster",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("K8S_MCP_SERVER_URL", "http://localhost:8082/mcp")
            )
        )
    ],
)

a2a_app = to_a2a(root_agent, port=9996, host="host.docker.internal")
