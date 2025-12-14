"""
Secure DevOps Agent with input/output security filtering
"""

import os
import re
from typing import Dict, Any
from google.adk.agents import Agent

# ----------------------------
# 1) Simple security filters
# ----------------------------
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----")
API_KEY_HINT_RE = re.compile(r"\b(?:sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{16})\b")  # common patterns

def reject_if_sensitive(text: str) -> Dict[str, Any]:
    """
    Gatekeeper for inbound text before it reaches the model context.
    This is intentionally simple for demo purposes.
    """
    if PRIVATE_KEY_RE.search(text) or API_KEY_HINT_RE.search(text):
        return {"ok": False, "reason": "Potential secret detected (key/token). Remove it and try again."}
    if EMAIL_RE.search(text):
        return {"ok": False, "reason": "Potential personal data detected (email). Remove it and try again."}
    return {"ok": True, "reason": "Clean"}

def redact_sensitive(text: str) -> str:
    """
    Redacts sensitive-looking strings in outbound content.
    """
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PRIVATE_KEY_RE.sub("[REDACTED_PRIVATE_KEY]", text)
    text = API_KEY_HINT_RE.sub("[REDACTED_KEY]", text)
    return text

# ----------------------------
# 2) Tools
# ----------------------------

def get_dummy_devops_metrics() -> str:
    """
    Get sample DevOps metrics for demonstration.
    Returns sanitized metrics data.
    """
    return """
    DevOps Metrics (Last 24h):
    - CPU Usage: 65%
    - Memory Usage: 72%
    - Active Pods: 24
    - Failed Deployments: 2
    - Airflow DAG Success Rate: 94%
    """

def trigger_airflow_dag(dag_id: str, reason: str) -> str:
    """
    Trigger an allowlisted Airflow DAG for demo purposes.
    
    Args:
        dag_id: The DAG ID to trigger (must be in allowlist)
        reason: Brief reason for triggering this DAG
    
    Returns:
        Status message about the trigger request
    """
    # Allowlist for safety
    ALLOWED_DAGS = ["example_failure_dag", "ml_model_downstream_dag", "prometheus_metrics_dag"]
    
    if dag_id not in ALLOWED_DAGS:
        return f"❌ DAG '{dag_id}' is not in the allowlist. Allowed DAGs: {', '.join(ALLOWED_DAGS)}"
    
    # In production, this would call actual Airflow API
    return f"✅ Trigger request submitted for DAG '{dag_id}'\nReason: {reason}\nStatus: Queued (demo mode)"

# ----------------------------
# 3) Root agent instructions
# ----------------------------
SECURITY_INSTRUCTION = """
You are a security-focused DevOps assistant running under strict security rules.

Non-negotiable rules:
- Do NOT request, accept, or output secrets (API keys, tokens, passwords, private keys).
- Do NOT request, accept, or output personal data (emails, phone numbers, IDs).
- You may analyze ONLY sanitized metrics/log snippets provided via tools.
- You may recommend actions, but any action must be via the allowed tool trigger_airflow_dag using only allowlisted DAG IDs.

When proposing operational actions:
- Prefer non-prod actions for demos.
- Always include a short risk note.
- Validate DAG IDs against the allowlist before triggering.

If the user asks for something out of scope, say what you can do safely instead.

Available capabilities:
- Get DevOps metrics (sanitized)
- Trigger allowlisted Airflow DAGs with justification
""".strip()

# Choose a model
MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash-exp")

root_agent = Agent(
    name="secure_devops_assistant",
    model=MODEL,
    description="A security-focused DevOps assistant with strict data protection rules",
    instruction=SECURITY_INSTRUCTION,
    tools=[get_dummy_devops_metrics, trigger_airflow_dag],
)
