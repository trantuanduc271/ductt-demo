import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from db_utils import (
    import_user_awareness_from_json,
    import_user_awareness_from_json_content,
    load_user_awareness_status_from_db,
    save_training_assignments_to_db,
    delete_user_from_db,
)


logger = logging.getLogger(__name__)

# Load .env from parent directory (agent/.env)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# User awareness status file (local to this folder) - for import
USER_AWARENESS_STATUS_FILE = Path(__file__).parent / "user_awareness_status.json"


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
# Awareness Agent Tools - consume and store user training status
# =============================================================================
def import_user_awareness_status(json_file_path: Optional[str] = None) -> dict:
    """Import user awareness status from JSON file into PostgreSQL database.
    
    Users can provide a JSON file with user training status, and this tool will
    import it into the database. The JSON structure should match user_awareness_status.json.
    
    Args:
        json_file_path: Path to JSON file. If not provided, uses default user_awareness_status.json
    
    Returns:
        Dictionary with import results (users_imported, status_updated, errors)
    """
    if json_file_path is None:
        json_file_path = str(USER_AWARENESS_STATUS_FILE)
    
    logger.info("Importing user awareness status from JSON: %s", json_file_path)
    return import_user_awareness_from_json(json_file_path)


def import_user_awareness_from_upload(json_content: str) -> dict:
    """Import user awareness status from uploaded JSON content into PostgreSQL database.
    
    This tool accepts JSON content directly (e.g., from file upload) and imports it.
    Use this when uploading files through the ADK web interface.
    
    Args:
        json_content: JSON string containing user awareness status data.
                     Should be an array of user objects with structure:
                     [{"user_id": "...", "name": "...", "department": "...", 
                       "region": "...", "overall_status": "...", 
                       "training_status": [...]}, ...]
    
    Returns:
        Dictionary with import results:
        - success: bool
        - users_imported: int
        - status_updated: int
        - errors: list (if any)
    """
    logger.info("Importing user awareness status from uploaded JSON content")
    return import_user_awareness_from_json_content(json_content)


def load_user_awareness_status() -> dict:
    """Load user awareness status from PostgreSQL database.
    
    This loads user training status data from the database (which was imported from JSON
    or updated by the agent). The data includes:
    - IdP attributes (department, region)
    - LMS/dashboard signals (last completion dates, status)
    - Operational status indicators
    
    Returns:
        Dictionary with 'users' list containing user training status records.
    """
    logger.info("Loading user awareness status from database")
    return load_user_awareness_status_from_db()


def save_training_assignments(
    assignments: List[Dict[str, Any]],
    approver_name: Optional[str] = None,
    approver_title: Optional[str] = None,
    approval_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Save approved training assignments to PostgreSQL database.
    
    This updates the database with new assignments, due dates, and approval metadata.
    Also creates audit log entries for compliance tracking.
    
    Args:
        assignments: List of assignment dicts with:
            - user_id: User identifier
            - module_id: Training module ID
            - due_date: Assignment due date (ISO format)
            - assigned_date: When assignment was created (optional)
            - linked_document: Policy document code (optional)
            - policy_citations: List of citations (optional)
        approver_name: Name of the approver
        approver_title: Title of the approver
        approval_date: Approval date in ISO format (if not provided, uses now)
    
    Returns:
        Dictionary with success status and updated record count.
    """
    logger.info("Saving %d training assignments to database", len(assignments))
    return save_training_assignments_to_db(
        assignments=assignments,
        approver_name=approver_name,
        approver_title=approver_title,
        approval_date=approval_date,
    )


def delete_user(user_id: str) -> dict:
    """Delete a user and all associated records from the database.
    
    This will permanently remove:
    - The user record
    - All training status records for the user
    - All training assignments for the user
    - All audit log entries for the user
    
    Use this when a user has left the organization or needs to be removed from the system.
    
    Args:
        user_id: The user_id of the user to delete (e.g., "u-001", "u-007")
    
    Returns:
        Dictionary with success status and deletion details:
        - success: bool
        - user_id: The deleted user_id
        - user_name: The name of the deleted user
        - deleted_records: Dict with counts of deleted records
        - error: Error message if deletion failed
    """
    logger.info("Deleting user %s from database", user_id)
    return delete_user_from_db(user_id)


# =============================================================================
# HITL Tool - approval for training assignments / document updates
# =============================================================================
async def request_assignment_approval(
    summary: str,
    risk_level: str = "medium",
) -> str:
    """Ask a human approver to review training assignments or document changes.

    Args:
        summary: Human-readable summary of:
                 - flagged users + gaps
                 - proposed assignments (modules, due dates)
                 - policy / standard citations
                 - any document changes requested
        risk_level: "low", "medium", "high" - informs how strong the language should be.

    Returns:
        Markdown text to present to the approver.
    """
    logger.info("HITL approval requested by awareness_agent (risk=%s)", risk_level)

    risk_emoji = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🔴",
    }.get(risk_level, "⚪")

    return (
        f"{risk_emoji} **APPROVAL REQUIRED – Security Training / Policy Action**\n\n"
        f"**Context summary:**\n{summary}\n\n"
        f"**Please respond with one of the following options:**\n"
        f"- `approve` – approve all listed assignments/changes as proposed\n"
        f"- `approve with changes: ...` – specify edits (due dates, modules, exceptions)\n"
        f"- `reject` – do not proceed; include brief reason\n"
        f"- Optionally include: approver name/title and any exception rationale for audit\n"
    )


# =============================================================================
# Awareness Agent System Instruction
# =============================================================================
AWARENESS_SYSTEM_INSTRUCTION = (
    "You are the Awareness/Training Agent for security and compliance.\n\n"
    "You focus on:\n"
    "- Consuming a small JSON/YAML-like mapping of people and their training signals "
    "(departments, regions, last completion dates, operational status).\n"
    "- Detecting gaps (OVERDUE or MISSING modules) based on the cadence and rules provided by the Library Agent.\n"
    "- Converting gaps into a concrete assignment plan, notifications, and audit-ready evidence.\n\n"
    "DATA CONSUMPTION:\n"
    "- Users can import JSON files in two ways:\n"
    "  1. File upload via ADK web: Use import_user_awareness_from_upload(json_content) when "
    "     a JSON file is uploaded through the web interface. Pass the file content as a string.\n"
    "  2. Local file path: Use import_user_awareness_status(json_file_path) to load from a "
    "     file path on the server.\n"
    "- ALWAYS start by calling load_user_awareness_status() to get the current user training status from database.\n"
    "- The database contains operational signals from dashboards, IdP attributes (department, region), "
    "and training completion status from LMS systems.\n"
    "- The data structure includes: user_id, name, department, region, overall_status, "
    "last_evaluated, and training_status array with module details.\n"
    "- After approval, use save_training_assignments() to persist new assignments to the database "
    "(this also creates audit log entries for compliance).\n"
    "- To remove a user from the system (e.g., when they leave the organization), use delete_user(user_id). "
    "This will permanently delete the user and all associated training records, assignments, and audit logs.\n\n"
    "STEP 1 – Awareness Agent detects gaps:\n"
    "- Compute which users are overdue or missing, following this pattern:\n"
    "    - Alice: Security Awareness overdue (2024-10-01 + 12m = 2025-10-01) → overdue on 2025-12-19\n"
    "    - Dave: GDPR Basics overdue (2023-11-20 + 12m = 2024-11-20) → overdue\n"
    "    - Carol: PCI Basics missing → overdue\n"
    "    - Bob: OK (Security Awareness due 2026-01-15)\n"
    "- Then ask the Library Agent (via its tool) which exact training modules apply and which policies justify them.\n\n"
    "STEP 2 – Library Agent lookups:\n"
    "- Call the library assistant tool to:\n"
    "    - Load approved modules and rules.\n"
    "    - Determine module IDs/titles per user.\n"
    "    - Fetch applicable policy/standard references (document IDs, sections, reasons).\n"
    "    - Determine required cadence.\n\n"
    "STEP 3 – Turn into an assignment plan:\n"
    "- Build, for each user:\n"
    "    - Assignment list (module IDs, titles).\n"
    "    - Due dates (by default, now + 14 days, unless the org specifies otherwise).\n"
    "    - Email/notification drafts explaining what and why, with citations.\n"
    "    - Evidence log entries for audit (user, module, due date, policy codes/sections, rule IDs).\n\n"
    "HUMAN-IN-THE-LOOP (HITL) APPROVAL:\n"
    "- MANDATORY: Before finalizing any assignments/notifications/evidence, you MUST call "
    "request_assignment_approval() with a concise summary. Do not mark assignments final "
    "or 'approved' unless the human explicitly approves.\n"
    "- If the user has not provided an explicit approval decision in this turn, call "
    "request_assignment_approval(), return the approval prompt, and mark all assignments as "
    "PENDING APPROVAL (do not show 'approved' audit records).\n"
    "- Only after the user replies with approval (or approval with changes) may you present "
    "finalized assignments/notifications/evidence with an approved audit record.\n"
    "  - Do not fabricate approvers, dates, or approval states.\n\n"
    "UPGRADE IDEAS YOU SUPPORT:\n"
    "- Automatic Version Summarization: when new policy/handbook content is provided, ask the Library Agent "
    "to summarize 'What's Changed' for a specific department and include that in notifications.\n"
    "- QA Chatbot Interface: when users ask natural language questions (e.g., 'What is our policy on remote "
    "work in Singapore?'), delegate to the Library Agent to answer with citations.\n"
    "- Sending notifications: always treat generated emails/messages as drafts; do not claim they were sent.\n\n"
    "OUTPUT FORMAT TO THE USER:\n"
    "- Use clear Markdown sections:\n"
    "    1. Awareness Summary (list of users and their gap status).\n"
    "    2. Proposed Assignments (table with user, role, module ID, title, status, due date).\n"
    "    3. Policy Citations & Evidence Log.\n"
    "    4. Notification Drafts.\n"
    "    5. Approval Status (Pending or Approved with details).\n"
    "- Example executive-friendly snippet after approval:\n"
    "    - Alice (HR EU): Annual Security Awareness + GDPR for HR (due Jan 9, 2026)\n"
    "    - Dave (HR EU): GDPR for HR (due Jan 9, 2026)\n"
    "    - Carol (Finance US): PCI Basics for Finance (due Jan 9, 2026)\n"
    "    - Approved by Compliance Manager on 2025-12-19 with policy citations.\n"
)


# Connect to Library Agent via A2A
library_base = os.getenv("LIBRARY_AGENT_BASE_URL", "http://localhost:9999")
library_remote_agent = RemoteA2aAgent(
    name="security_training_library",
    description=(
        "Library/Knowledge agent for security training. "
        "Looks up approved modules, cadences, and policy/library content; "
        "provides policy basis and QA over the training library."
    ),
    agent_card=f"{library_base}{AGENT_CARD_WELL_KNOWN_PATH}",
)


model_name = os.getenv("AWARENESS_AGENT_MODEL", "gemini-3-pro-preview")

generate_content_config = types.GenerateContentConfig(
    temperature=_env_float("AWARENESS_AGENT_TEMPERATURE", 0.0),
    top_p=_env_float("AWARENESS_AGENT_TOP_P", 0.95),
    top_k=_env_int("AWARENESS_AGENT_TOP_K", None),
    max_output_tokens=_env_int("AWARENESS_AGENT_MAX_OUTPUT_TOKENS", 8192),
)

logger.info(
    "awareness_agent config: model=%s temperature=%s top_p=%s top_k=%s max_output_tokens=%s",
    model_name,
    generate_content_config.temperature,
    generate_content_config.top_p,
    generate_content_config.top_k,
    generate_content_config.max_output_tokens,
)


# Awareness/Training agent (exposed externally)
awareness_agent = Agent(
    model=model_name,
    name="awareness_agent",
    description=(
        "Awareness/Training agent that consumes operational training signals, "
        "detects gaps, coordinates with the Library agent, and uses HITL approval "
        "to produce assignments, notifications, and audit-ready evidence."
    ),
    instruction=AWARENESS_SYSTEM_INSTRUCTION,
    generate_content_config=generate_content_config,
    tools=[
        FunctionTool(import_user_awareness_status),
        FunctionTool(import_user_awareness_from_upload),
        FunctionTool(load_user_awareness_status),
        FunctionTool(save_training_assignments),
        FunctionTool(delete_user),
        AgentTool(library_remote_agent),
        FunctionTool(request_assignment_approval),
    ],
)

# Expose the Awareness agent as A2A app for remote_a2a_agent orchestration.
a2a_app = to_a2a(awareness_agent, port=int(os.getenv("AWARENESS_AGENT_PORT", "9998")), host="localhost")

