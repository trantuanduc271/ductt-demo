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
    "You are a Kubernetes cluster management assistant with direct access to a Kubernetes cluster via MCP tools. "
    "You have all necessary credentials and configuration already loaded and must rely on your tools for any "
    "cluster information or actions instead of guessing.\n\n"
    "Your goals are: (1) be reliable and consistent between runs, (2) be safe with cluster-changing actions, and "
    "(3) explain what you are doing in a clear, structured way.\n\n"
    "You can help with:\n"
    "- Listing and managing namespaces, nodes, pods, deployments, services, and other Kubernetes resources\n"
    "- Viewing pod logs and events\n"
    "- Checking resource status and details\n"
    "- Creating, updating, and deleting Kubernetes resources (but confirm destructive actions with the user first)\n"
    "- Executing commands in pods\n"
    "- Managing Helm releases\n\n"
    "IMPORTANT behavior rules for consistency:\n"
    "- Always follow this answer structure:\n"
    "  1. Short summary of the user's request\n"
    "  2. Plan: bullet list of the steps you will take\n"
    "  3. Execution: tool calls and results, explained in natural language\n"
    "  4. Final answer: clear recommendation or outcome\n"
    "- Always use MCP tools to inspect the cluster before giving a final answer.\n"
    "- If information is missing or ambiguous, explicitly say what is missing instead of inventing details.\n\n"
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
    "Formatting rules:\n"
    "- Always provide clear, well-formatted responses in Markdown.\n"
    "- Use headings for major sections (Summary, Plan, Execution, Result).\n"
    "- When showing resource details, organize information logically with tables or bullet lists."
)

# Allow overriding the model via environment; default to a higher-quality Pro model for better reasoning
model_name = os.getenv("K8S_AGENT_MODEL", "gemini-3-pro-preview")

# Generation settings (controls consistency):
# - Set K8S_AGENT_TEMPERATURE=0 for the most deterministic output.
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
    temperature=_env_float("K8S_AGENT_TEMPERATURE", 0.0),
    top_p=_env_float("K8S_AGENT_TOP_P", 0.95),
    top_k=_env_int("K8S_AGENT_TOP_K", None),
    # Increase max_output_tokens to handle detailed pod logs, events, and resource listings
    # Default to 16384 (16k tokens) for complex Kubernetes operations, can be overridden via env var
    max_output_tokens=_env_int("K8S_AGENT_MAX_OUTPUT_TOKENS", 16384),
)

# Log effective generation config at startup so it's easy to verify via server logs.
logger.info(
    "Kubernetes agent generation config: model=%s temperature=%s top_p=%s top_k=%s max_output_tokens=%s",
    model_name,
    generate_content_config.temperature,
    generate_content_config.top_p,
    generate_content_config.top_k,
    generate_content_config.max_output_tokens,
)

# Also log effective generation config at the start of each turn (useful for multi-turn debugging).
# In some ADK versions, CallbackContext doesn't expose `agent`, so log from our known config.
async def _log_generation_config(callback_context):
    try:
        payload = (
            generate_content_config.model_dump()
            if hasattr(generate_content_config, "model_dump")
            else generate_content_config
        )
        logger.info("kubernetes_bot turn generate_content_config=%s", payload)
    except Exception:
        logger.exception("Failed to log kubernetes_bot generate_content_config")
    return None


async def _log_agent_response(callback_context):
    """Log agent responses to detect token limit issues."""
    try:
        max_tokens = generate_content_config.max_output_tokens or 16384
        chars_per_token = 4  # Rough estimate: 1 token ≈ 4 characters
        
        if hasattr(callback_context, "response"):
            response = callback_context.response
            logger.info("kubernetes_bot response received, type=%s", type(response).__name__)
            
            if hasattr(response, "text"):
                text_len = len(response.text) if response.text else 0
                estimated_tokens = text_len / chars_per_token
                logger.info("kubernetes_bot response text length=%d chars (~%d tokens, max=%d)", 
                           text_len, int(estimated_tokens), max_tokens)
                
                if estimated_tokens >= max_tokens * 0.9:
                    logger.warning("kubernetes_bot response may be approaching token limit! "
                                  "Estimated tokens: %d / %d (%.1f%%)", 
                                  int(estimated_tokens), max_tokens,
                                  (estimated_tokens / max_tokens) * 100)
                
                if response.text:
                    truncation_indicators = ["...", "[truncated]", "[cut off]", "incomplete"]
                    if any(indicator in response.text[-100:].lower() for indicator in truncation_indicators):
                        logger.warning("kubernetes_bot response may be truncated!")
    except Exception as e:
        logger.exception("Failed to log kubernetes_bot response: %s", e)
    return None

# This agent can be used standalone or as a sub-agent in a multi-agent system.
root_agent = Agent(
    model=model_name,
    name="kubernetes_assistant",
    description="An assistant that can help you with your Kubernetes cluster",
    instruction=SYSTEM_INSTRUCTION,
    generate_content_config=generate_content_config,
    before_agent_callback=_log_generation_config,
    after_agent_callback=_log_agent_response,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("K8S_MCP_SERVER_URL", "http://localhost:8082/mcp")
            )
        )
    ],
)

a2a_app = to_a2a(root_agent, port=9996, host="localhost")
