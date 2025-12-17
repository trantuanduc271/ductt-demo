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
    "You are a specialized assistant for managing Apache Airflow. "
    "Your purpose is to help users interact with their Airflow instance using the available MCP tools. "
    "You can help with:\n"
    "- Listing, pausing, unpausing, and managing DAGs\n"
    "- Triggering and monitoring DAG runs\n"
    "- Viewing task instances and their logs\n"
    "- Managing Airflow variables, connections, and pools\n"
    "- Checking Airflow health and monitoring\n"
    "- Working with datasets and XComs\n\n"
    "Always provide clear, helpful responses about Airflow operations. "
    "When you trigger a DAG, provide the DAG run ID and timestamp so users can correlate with Kubernetes pods. "
    "If the user asks about topics unrelated to Airflow management, "
    "politely state that you can only assist with Apache Airflow operations."
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

