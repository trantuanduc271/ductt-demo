import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool

# Load .env from parent directory (agent/.env)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


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


# =============================================================================
# APPROVAL TOOL - Human-in-the-Loop
# =============================================================================
async def request_user_approval(
    action: str,
    details: str,
    risk_level: str = "medium"
) -> str:
    """
    Request approval from the user before proceeding with an action.
    
    Args:
        action: The action requiring approval (e.g., "Trigger DAG", "Delete pod")
        details: Detailed description of what will happen
        risk_level: Risk level - "low", "medium", or "high"
    
    Returns:
        Approval status message to present to the user
    """
    logger.info(f"Approval requested: {action} (risk: {risk_level})")
    logger.info(f"Details: {details}")
    
    # Return a message that prompts the user to approve or reject
    risk_emoji = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🔴"
    }.get(risk_level, "⚪")
    
    return (
        f"{risk_emoji} **APPROVAL REQUIRED**\n\n"
        f"**Action:** {action}\n"
        f"**Risk Level:** {risk_level.upper()}\n\n"
        f"**Details:**\n{details}\n\n"
        f"**Please respond with:**\n"
        f"- `approve` or `yes` to proceed\n"
        f"- `reject` or `no` to cancel\n"
    )


ROOT_SYSTEM_INSTRUCTION = (
    "You are a DevOps orchestrator that coordinates between Airflow, Kubernetes, and Security Training systems.\n\n"
    "AVAILABLE TOOLS:\n"
    "1. airflow_assistant - Manages Apache Airflow DAGs, runs, tasks, and logs\n"
    "2. kubernetes_assistant - Manages Kubernetes pods, deployments, services, logs, and events\n"
    "3. awareness_agent - Awareness/Training agent (Agent 1) for security and compliance:\n"
    "   - Detects training gaps and overdue assignments\n"
    "   - Plans training assignments with policy citations\n"
    "   - Imports user awareness status from JSON data\n"
    "   - Requests HITL approval for training assignments\n"
    "   - Can delegate to security_training_library for policy lookups\n"
    "4. security_training_library - Library/Knowledge agent (Agent 2) for policy and training content:\n"
    "   - Searches policy documents using semantic similarity (vector DB)\n"
    "   - Loads training catalog and assignment rules\n"
    "   - Retrieves policy text content with citations\n"
    "   - Answers questions like 'List all mandatory training' or 'Summary AI policy'\n"
    "5. request_user_approval - Request human approval for destructive or sensitive operations\n\n"
    "SECURITY TRAINING WORKFLOW:\n"
    "For security training queries, you can use either agent:\n"
    "- Use awareness_agent for: gap detection, assignment planning, approvals, data import\n"
    "- Use security_training_library for: policy queries, training catalog lookups, document searches\n"
    "- The awareness agent can also call the library internally, but you can call both directly for visibility\n\n"
    "JSON DATA IMPORT:\n"
    "When a user pastes or provides JSON data (e.g., user awareness status JSON):\n"
    "1. Extract the JSON content from the user's message\n"
    "2. Call security_training_orchestrator's import_user_awareness_from_upload tool\n"
    "3. Pass the JSON content as a string to the json_content parameter\n"
    "4. The tool will import the data into the PostgreSQL database\n"
    "Example: User pastes JSON → Call security_training_orchestrator.import_user_awareness_from_upload(json_content=<pasted_json_string>)\n\n"
    "APPROVAL WORKFLOW:\n"
    "For DESTRUCTIVE or SENSITIVE operations, you MUST request approval BEFORE executing:\n\n"
    "Operations requiring APPROVAL:\n"
    "- Triggering DAGs (medium risk)\n"
    "- Deleting resources (high risk)\n"
    "- Modifying configurations (medium risk)\n"
    "- Restarting services (medium risk)\n"
    "- Scaling operations (low-medium risk)\n\n"
    "Operations NOT requiring approval:\n"
    "- Listing/viewing resources (read-only)\n"
    "- Getting logs or status (read-only)\n"
    "- Health checks (read-only)\n\n"
    "APPROVAL PATTERN:\n"
    "1. User requests action: 'Trigger example_failure_dag'\n"
    "2. You call request_user_approval tool:\n"
    "   - action='Trigger DAG example_failure_dag'\n"
    "   - details='This will trigger a new run of example_failure_dag in namespace airflow-3'\n"
    "   - risk_level='medium'\n"
    "3. Present approval request to user\n"
    "4. Wait for user response (approve/reject)\n"
    "5. If approved: proceed with airflow_assistant tool\n"
    "6. If rejected: acknowledge and stop\n\n"
    "WORKFLOW PATTERNS:\n\n"
    "Single-System Queries:\n"
    "- Airflow only: 'List all DAGs' → Use airflow_assistant tool (no approval needed)\n"
    "- Kubernetes only: 'List pods' → Use kubernetes_assistant tool (no approval needed)\n\n"
    "Cross-System Queries with Approval:\n"
    "When a query involves TRIGGERING DAGs AND viewing pods:\n\n"
    "1. First call request_user_approval for the trigger action\n"
    "2. Wait for user to approve\n"
    "3. If approved, call airflow_assistant to trigger DAG\n"
    "4. Get response with: dag_id, dag_run_id, execution_date, namespace, state\n"
    "5. Then call kubernetes_assistant with the Airflow info\n"
    "6. Combine both responses\n\n"
    "EXAMPLES:\n\n"
    "Example 1: Read-only query (no approval)\n"
    "User: 'List all DAGs'\n"
    "You: Call airflow_assistant directly\n\n"
    "Example 2: Destructive action (requires approval)\n"
    "User: 'Trigger example_failure_dag'\n"
    "You: \n"
    "  1. Call request_user_approval(\n"
    "       action='Trigger DAG example_failure_dag',\n"
    "       details='This will start a new DAG run in namespace airflow-3',\n"
    "       risk_level='medium'\n"
    "     )\n"
    "  2. Present approval request to user\n"
    "  3. Wait for user response\n"
    "User: 'approve'\n"
    "You: Call airflow_assistant to trigger the DAG\n\n"
    "Example 3: Complex workflow with approval\n"
    "User: 'Trigger example_failure_dag and show me which pod is running it'\n"
    "You:\n"
    "  1. Call request_user_approval for the trigger\n"
    "  2. Wait for approval\n"
    "  3. If approved: Call airflow_assistant to trigger DAG\n"
    "  4. Get dag_run_id, namespace, etc.\n"
    "  5. Call kubernetes_assistant to find pod\n"
    "  6. Combine responses\n\n"
    "RESPONSE FORMAT:\n"
    "- Use Markdown with clear sections\n"
    "- For approval requests: Present the risk level and details clearly\n"
    "- After approval: Proceed with the operation and report results\n"
    "- If rejected: Acknowledge and suggest alternative read-only operations\n"
)


airflow_base = os.getenv("AIRFLOW_A2A_BASE_URL", "http://localhost:9997")
k8s_base = os.getenv("K8S_A2A_BASE_URL", "http://localhost:9996")
awareness_base = os.getenv("AWARENESS_AGENT_BASE_URL", "http://localhost:9998")
library_base = os.getenv("LIBRARY_AGENT_BASE_URL", "http://localhost:9999")

airflow_remote_agent = RemoteA2aAgent(
    name="airflow_assistant",
    description=(
        "Manages Apache Airflow workflows. "
        "Use for: listing DAGs, triggering DAG runs, checking task status, "
        "getting DAG run history, viewing task logs, managing Airflow health."
    ),
    agent_card=f"{airflow_base}{AGENT_CARD_WELL_KNOWN_PATH}",
)

k8s_remote_agent = RemoteA2aAgent(
    name="kubernetes_assistant",
    description=(
        "Manages Kubernetes resources. "
        "Use for: listing pods, getting pod logs, checking pod events, "
        "viewing deployments/services, monitoring cluster health, finding pods by labels."
    ),
    agent_card=f"{k8s_base}{AGENT_CARD_WELL_KNOWN_PATH}",
)

awareness_remote_agent = RemoteA2aAgent(
    name="awareness_agent",
    description=(
        "Awareness/Training agent (Agent 1) for security and compliance. "
        "Use for: awareness gap detection, training assignment planning, policy citations, HITL approvals, "
        "and importing user awareness status from JSON data into the database."
    ),
    agent_card=f"{awareness_base}{AGENT_CARD_WELL_KNOWN_PATH}",
)

library_remote_agent = RemoteA2aAgent(
    name="security_training_library",
    description=(
        "Library/Knowledge agent (Agent 2) for policy and training content. "
        "Use for: semantic policy searches, training catalog lookups, document retrieval, "
        "answering questions like 'List all mandatory training' or 'Summary AI policy'."
    ),
    agent_card=f"{library_base}{AGENT_CARD_WELL_KNOWN_PATH}",
)


root_model_name = os.getenv("ROOT_AGENT_MODEL", "gemini-3-pro-preview")

generate_content_config = types.GenerateContentConfig(
    temperature=_env_float("ROOT_AGENT_TEMPERATURE", 0.0),
    top_p=_env_float("ROOT_AGENT_TOP_P", 0.95),
    top_k=_env_int("ROOT_AGENT_TOP_K", None),
    max_output_tokens=_env_int("ROOT_AGENT_MAX_OUTPUT_TOKENS", 8192),
)

logger.info(
    "Root DevOps agent config: model=%s temp=%s top_p=%s top_k=%s max_tokens=%s",
    root_model_name,
    generate_content_config.temperature,
    generate_content_config.top_p,
    generate_content_config.top_k,
    generate_content_config.max_output_tokens,
)


async def _log_generation_config(callback_context):
    try:
        payload = (
            generate_content_config.model_dump()
            if hasattr(generate_content_config, "model_dump")
            else generate_content_config
        )
        logger.info("devops_root turn config: %s", payload)
    except Exception:
        logger.exception("Failed to log config")
    return None


async def _log_agent_response(callback_context):
    try:
        max_tokens = generate_content_config.max_output_tokens or 8192
        chars_per_token = 4
        
        if hasattr(callback_context, "response"):
            response = callback_context.response
            
            if hasattr(response, "text") and response.text:
                text_len = len(response.text)
                estimated_tokens = text_len / chars_per_token
                logger.info(
                    "devops_root response: %d chars (~%d tokens, max=%d)",
                    text_len, int(estimated_tokens), max_tokens
                )
                
                if estimated_tokens >= max_tokens * 0.9:
                    logger.warning(
                        "Response approaching token limit: %d/%d (%.1f%%)",
                        int(estimated_tokens), max_tokens,
                        (estimated_tokens / max_tokens) * 100
                    )
    except Exception:
        logger.exception("Failed to log response")
    return None


root_agent = Agent(
    model=root_model_name,
    name="devops_root",
    description="DevOps orchestrator for Airflow and Kubernetes operations with approval workflow",
    instruction=ROOT_SYSTEM_INSTRUCTION,
    generate_content_config=generate_content_config,
    before_agent_callback=_log_generation_config,
    after_agent_callback=_log_agent_response,
    tools=[
        FunctionTool(request_user_approval),
        AgentTool(airflow_remote_agent),
        AgentTool(k8s_remote_agent),
        AgentTool(awareness_remote_agent),
        AgentTool(library_remote_agent),
    ],
)