import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Load .env from parent directory (agent/.env)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

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

# Allow overriding the model via environment; default to a higher-quality Pro model for better reasoning
model_name = os.getenv("AIRFLOW_AGENT_MODEL", "gemini-2.5-pro")

# Generation settings (controls consistency):
# - Set AIRFLOW_AGENT_TEMPERATURE=0 for the most deterministic output.
# - Optionally tune TOP_P / TOP_K / MAX_OUTPUT_TOKENS.
def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return float(value)


def _env_int(name: str, default: int | None) -> int | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


generate_content_config = types.GenerateContentConfig(
    temperature=_env_float("AIRFLOW_AGENT_TEMPERATURE", 0.0),
    top_p=_env_float("AIRFLOW_AGENT_TOP_P", 0.95),
    top_k=_env_int("AIRFLOW_AGENT_TOP_K", None),
    max_output_tokens=_env_int("AIRFLOW_AGENT_MAX_OUTPUT_TOKENS", None),
)

# Log effective generation config at startup so it's easy to verify via server logs.
logger.info(
    "Airflow agent generation config: model=%s temperature=%s top_p=%s top_k=%s max_output_tokens=%s",
    model_name,
    generate_content_config.temperature,
    generate_content_config.top_p,
    generate_content_config.top_k,
    generate_content_config.max_output_tokens,
)

# Also log effective generation config at the start of each turn (useful for multi-turn debugging).
async def _log_generation_config(callback_context):
    try:
        payload = (
            generate_content_config.model_dump()
            if hasattr(generate_content_config, "model_dump")
            else generate_content_config
        )
        logger.info("airflow_bot turn generate_content_config=%s", payload)
    except Exception:
        logger.exception("Failed to log airflow_bot generate_content_config")
    return None

# This agent can be used standalone or as a sub-agent in a multi-agent system
root_agent = Agent(
    model=model_name,
    name="airflow_assistant",
    description="An assistant that can help manage Apache Airflow workflows and operations",
    instruction=SYSTEM_INSTRUCTION,
    generate_content_config=generate_content_config,
    before_agent_callback=_log_generation_config,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
            )
        )
    ],
)

a2a_app = to_a2a(root_agent, port=9997, host="localhost")

