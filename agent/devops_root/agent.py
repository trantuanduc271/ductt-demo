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
from google.adk.a2a.utils.agent_to_a2a import to_a2a


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


ROOT_SYSTEM_INSTRUCTION = (
    "You are a DevOps root assistant that coordinates between an Apache Airflow agent "
    "and a Kubernetes agent, both exposed as remote A2A agents.\n\n"
    "Your goals are:\n"
    "1. Understand what the user wants at a high level.\n"
    "2. Decide whether to call the Airflow agent, the Kubernetes agent, or both in sequence.\n"
    "3. Orchestrate multi-step flows across both systems and return a single, clear answer.\n\n"
    "Sub-agents:\n"
    "- airflow_assistant: For DAGs, DAG runs, tasks, logs, history, and Airflow health.\n"
    "- kubernetes_assistant: For pods, deployments, services, namespaces, logs, and events.\n\n"
    "CRITICAL RULE (Airflow + Kubernetes together):\n"
    "- If a user request involves both DAGs/tasks/Airflow AND pods/logs/events/namespaces/Kubernetes, you MUST:\n"
    "  1) ALWAYS delegate to airflow_assistant first (to trigger or locate the DAG run and get identifiers + timestamps).\n"
    "  2) AFTER that, you MUST delegate to kubernetes_assistant using those identifiers/timestamps to find pods and fetch logs/events.\n"
    "  3) You are NOT allowed to answer such a request using only Airflow; you must show results from kubernetes_assistant as well.\n"
    "  4) If you are unsure whether the user cares about pods/logs, err on the side of ALSO calling kubernetes_assistant.\n\n"
    "Playbook example (you MUST follow this pattern for similar requests):\n"
    "- User says: 'Trigger DAG sales_analytics_pipeline now, wait until it starts, then find the pod(s) running its tasks and show logs + events for any failed task.'\n"
    "  Step A (Airflow):\n"
    "    - Delegate to airflow_assistant.\n"
    "    - Ask it to trigger or locate the DAG run and return a JSON summary with: dag_id, dag_run_id or run_id,\n"
    "      execution_date/logical_date (ISO 8601), namespace (e.g. airflow-3), and for each relevant task:\n"
    "      task_id, state, start_date, try_number.\n"
    "  Step B (Kubernetes):\n"
    "    - Then delegate to kubernetes_assistant.\n"
    "    - Pass that JSON summary in your prompt and ask it to find matching pod(s) using namespace and labels\n"
    "      (dag_id, task_id, run_id) and creation timestamps; then fetch pod logs and events for the best match.\n"
    "  Step C (Final answer):\n"
    "    - Combine the Airflow JSON and Kubernetes findings into ONE Markdown answer with sections:\n"
    "      'Summary', 'Airflow Details', 'Kubernetes Details', and 'Next Steps'.\n\n"
    "General delegation rules:\n"
    "- If the question is only about DAGs, tasks, or Airflow metadata → delegate only to airflow_assistant (never answer purely by yourself).\n"
    "- If the question is only about pods, deployments, services, or cluster state → delegate only to kubernetes_assistant (never answer purely by yourself).\n"
    "- If the question mentions both DAGs/tasks and pods/logs/namespaces/Kubernetes → you MUST run Airflow then Kubernetes as above, even if you think one system is enough.\n\n"
    "Output formatting:\n"
    "- Always respond in Markdown.\n"
    "- Use headings like 'Summary', 'Airflow Details', 'Kubernetes Details', and 'Next Steps' when appropriate.\n"
    "- Clearly label which information comes from Airflow vs from Kubernetes.\n"
)


# Remote A2A sub-agents: point at your existing Airflow and K8s A2A servers.
# NOTE: This process (devops_root) runs on your host alongside the other agents,
# so the sensible default is localhost. Your UI in Docker should still use
# host.docker.internal to reach this root agent.
airflow_base = os.getenv("AIRFLOW_A2A_BASE_URL", "http://localhost:9997")
k8s_base = os.getenv("K8S_A2A_BASE_URL", "http://localhost:9996")

airflow_remote_agent = RemoteA2aAgent(
    name="airflow_assistant",
    description="Remote Airflow assistant accessed via A2A.",
    agent_card=f"{airflow_base}{AGENT_CARD_WELL_KNOWN_PATH}",
)

k8s_remote_agent = RemoteA2aAgent(
    name="kubernetes_assistant",
    description="Remote Kubernetes assistant accessed via A2A.",
    agent_card=f"{k8s_base}{AGENT_CARD_WELL_KNOWN_PATH}",
)


# Root model + generation config
root_model_name = os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-pro")

generate_content_config = types.GenerateContentConfig(
    temperature=_env_float("ROOT_AGENT_TEMPERATURE", 0.0),
    top_p=_env_float("ROOT_AGENT_TOP_P", 0.95),
    top_k=_env_int("ROOT_AGENT_TOP_K", None),
    max_output_tokens=_env_int("ROOT_AGENT_MAX_OUTPUT_TOKENS", None),
)

logger.info(
    "Root DevOps agent generation config: model=%s temperature=%s top_p=%s top_k=%s max_output_tokens=%s",
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
        logger.info("devops_root turn generate_content_config=%s", payload)
    except Exception:
        logger.exception("Failed to log devops_root generate_content_config")
    return None


root_agent = Agent(
    model=root_model_name,
    name="devops_root",
    description="A DevOps root agent that coordinates between Airflow and Kubernetes remote agents.",
    instruction=ROOT_SYSTEM_INSTRUCTION,
    generate_content_config=generate_content_config,
    before_agent_callback=_log_generation_config,
    sub_agents=[
        airflow_remote_agent,
        k8s_remote_agent,
    ],
)


ROOT_AGENT_PORT = int(os.getenv("ROOT_AGENT_PORT", "9995"))

# The `host` here is used in the agent card URL, not the bind address for uvicorn.
# Since your UI runs in Docker, it should reach this agent via host.docker.internal.
a2a_app = to_a2a(root_agent, port=ROOT_AGENT_PORT, host="host.docker.internal")


