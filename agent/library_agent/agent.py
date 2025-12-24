import os
import json
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Try to import vector DB (optional)
try:
    from vector_db import (
        search_documents, 
        list_indexed_documents, 
        get_full_document_content,
        CHROMADB_AVAILABLE
    )
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("Vector DB not available. Install chromadb for semantic search.")
    get_full_document_content = None


logger = logging.getLogger(__name__)

# Load .env from parent directory (agent/.env)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Data files - use documents folder for organization
BASE_DIR = Path(__file__).parent
DOCUMENTS_DIR = BASE_DIR / "documents"
CATALOG_FILE = DOCUMENTS_DIR / "training_catalog.txt"
RULES_FILE = DOCUMENTS_DIR / "training_rules.txt"

# Policy text files - prefer .txt in documents folder, fallback to root
POLICY_TEXT_FILES = {
    "POL-SEC-001": DOCUMENTS_DIR / "Information_Security_Policy.txt",
    "HR-HB-001": DOCUMENTS_DIR / "Human_Resources_Employee_Handbook.txt",
    "POL-AI-001": DOCUMENTS_DIR / "AI_and_Automated_Decision_Making_Policy.txt",
}

# Fallback to root folder if not in documents
for code, path in list(POLICY_TEXT_FILES.items()):
    if not path.exists():
        # Try root folder as fallback
        fallback_path = BASE_DIR / path.name
        if fallback_path.exists():
            POLICY_TEXT_FILES[code] = fallback_path
        else:
            logger.warning(f"Policy file not found: {path} or {fallback_path}")


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
# Library Agent Tools
# =============================================================================
def load_training_library(use_vector_db: bool = True) -> dict:
    """Return approved training catalog and assignment rules as structured JSON.
    
    Uses vector DB by default (recommended), falls back to files if vector DB unavailable.
    
    Args:
        use_vector_db: If True, retrieve from vector DB; if False, use file-based
    
    Returns:
        Dictionary with:
        - catalog: Training catalog JSON
        - rules: Training rules JSON
        - source: "vector_db" or "file"
    """
    logger.info("Loading training catalog and rules for library_agent")
    
    # Try vector DB first (if available and enabled)
    if use_vector_db and CHROMADB_AVAILABLE and get_full_document_content:
        try:
            # Get catalog from vector DB
            catalog_content = get_full_document_content("TRAINING-CATALOG")
            rules_content = get_full_document_content("TRAINING-RULES")
            
            if catalog_content and rules_content:
                try:
                    catalog = json.loads(catalog_content)
                    rules = json.loads(rules_content)
                    logger.info("Loaded training library from vector DB")
                    return {
                        "catalog": catalog,
                        "rules": rules,
                        "source": "vector_db",
                    }
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from vector DB: {e}, falling back to files")
        except Exception as e:
            logger.warning(f"Failed to load from vector DB: {e}, falling back to files")
    
    # Fallback to files
    try:
        with CATALOG_FILE.open("r", encoding="utf-8") as f:
            catalog = json.loads(f.read())

        with RULES_FILE.open("r", encoding="utf-8") as f:
            rules = json.loads(f.read())

        logger.info("Loaded training library from files")
        return {
            "catalog": catalog,
            "rules": rules,
            "source": "file",
        }
    except Exception as e:
        logger.exception(f"Failed to load training library from files: {e}")
        return {
            "catalog": [],
            "rules": {},
            "source": "error",
            "error": str(e),
        }


def search_policy_semantic(query: str, n_results: int = 5, document_code: Optional[str] = None) -> dict:
    """Search policy documents using semantic similarity (vector search).
    
    This tool uses vector embeddings to find relevant sections in policy documents
    based on meaning, not just keyword matching. Use this for questions like:
    - "What is our policy on remote work?"
    - "What are the requirements for data encryption?"
    - "Summary of AI governance"
    
    Args:
        query: Natural language search query
        n_results: Number of results to return (default 5)
        document_code: Optional filter by specific document (e.g., "POL-SEC-001")
    
    Returns:
        Dictionary with search results containing:
        - results: List of matching document chunks with content, title, document_code
        - query: The search query used
        - count: Number of results found
    """
    if not CHROMADB_AVAILABLE:
        return {
            "error": "Vector search not available. Install chromadb: pip install chromadb",
            "results": [],
            "count": 0
        }
    
    logger.info("Searching policy documents using semantic similarity (vector DB)")
    try:
        results = search_documents(
            query=query,
            n_results=n_results,
            document_code=document_code
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.exception(f"Vector search failed: {e}")
        return {
            "error": str(e),
            "results": [],
            "count": 0
        }


def load_policy_texts(max_chars: int = 50000, use_vector_db: bool = True) -> dict:
    """Return policy/handbook content keyed by document_code.
    
    Uses vector DB by default (recommended), falls back to files if vector DB unavailable.
    
    Args:
        max_chars: Maximum characters to return per document (default 50000 for full documents)
        use_vector_db: If True, retrieve from vector DB; if False, use file-based
    
    Returns:
        Dictionary with document_code as key, containing:
        - path: filename or "vector_db"
        - content: full or truncated text
        - truncated: boolean indicating if content was truncated
        - size: total character count
        - source: "vector_db" or "file"
    """
    logger.info("Loading policy text content for library_agent")
    payload = {}
    
    # Try vector DB first (if available and enabled)
    if use_vector_db and CHROMADB_AVAILABLE and get_full_document_content:
        logger.info("Retrieving policy content from vector DB")
        for code in POLICY_TEXT_FILES.keys():
            try:
                full_content = get_full_document_content(code)
                if full_content:
                    is_truncated = len(full_content) > max_chars
                    payload[code] = {
                        "path": "vector_db",
                        "content": full_content[:max_chars] if is_truncated else full_content,
                        "truncated": is_truncated,
                        "size": len(full_content),
                        "source": "vector_db",
                    }
                    if is_truncated:
                        logger.warning(f"Policy {code} truncated to {max_chars} chars (total: {len(full_content)})")
                    continue
            except Exception as e:
                logger.warning(f"Failed to load {code} from vector DB: {e}, falling back to file")
    
    # Fallback to files (for missing documents or if vector DB disabled)
    for code, path in POLICY_TEXT_FILES.items():
        if code in payload:  # Already loaded from vector DB
            continue
            
        if not path.exists():
            logger.warning(f"Policy file not found: {path} for code {code}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
            is_truncated = len(text) > max_chars
            payload[code] = {
                "path": path.name,
                "content": text[:max_chars] if is_truncated else text,
                "truncated": is_truncated,
                "size": len(text),
                "source": "file",
            }
            if is_truncated:
                logger.warning(f"Policy {code} truncated to {max_chars} chars (total: {len(text)})")
        except Exception as e:
            logger.exception(f"Failed to load policy {code} from {path}: {e}")
            payload[code] = {
                "path": path.name,
                "content": "",
                "truncated": False,
                "size": 0,
                "error": str(e),
                "source": "file",
            }
    return payload


# =============================================================================
# Library Agent System Instruction
# =============================================================================
LIBRARY_SYSTEM_INSTRUCTION = (
    "You are the Library/Knowledge Agent for security training.\n\n"
    "You are responsible for:\n"
    "- Loading and interpreting the training catalog and assignment rules via your tools.\n"
    "- Looking up approved training modules, their cadence, and linked policy/standard references.\n"
    "- Providing evidence/policy basis for why a module applies (document_code, section, reason).\n"
    "- Answering policy/library questions and summarizing changes in updated documents.\n\n"
    "TOOLS YOU HAVE:\n"
    "- load_training_library(): returns catalog + rules as structured JSON (from files).\n"
    "- load_policy_texts(): returns full text for policy/handbook documents (from vector DB by default).\n"
    "- search_policy_semantic(): **USE THIS for natural language questions** - semantic search over all documents in vector DB.\n\n"
    "WHEN TO USE WHICH TOOL:\n"
    "- For structured queries (list mandatory training, find module by ID): use load_training_library()\n"
    "- For specific document lookup: use load_policy_texts() with document_code\n"
    "- For natural language questions (\"What is our policy on X?\", \"Summary of Y\", \"Explain Z\"): **ALWAYS USE search_policy_semantic() FIRST**\n"
    "- If the query asks about policy content, requirements, or explanations: **USE search_policy_semantic()**\n"
    "- Vector DB (search_policy_semantic) is faster and more accurate for semantic questions than loading full documents\n\n"
    "CAPABILITIES:\n"
    "- Given user role/department/region, determine which modules are required using rules.\n"
    "- Given module IDs, explain the policy basis with citations (e.g., POL-SEC-001 Sec 6).\n"
    "- Answer semantic questions using vector search (e.g., 'What is our policy on remote work?').\n"
    "- Generate 'What's Changed' summaries between versions of policy/handbook text.\n\n"
    "OUTPUT FORMAT:\n"
    "- Prefer concise structured answers (tables/lists) with clear citations when giving policy basis.\n"
    "- When used by another agent, be deterministic and avoid changing IDs or inventing new modules.\n"
    "- For semantic search results, cite the document_code and provide relevant excerpts.\n"
)


model_name = os.getenv("LIBRARY_AGENT_MODEL", "gemini-3-pro-preview")

generate_content_config = types.GenerateContentConfig(
    temperature=_env_float("LIBRARY_AGENT_TEMPERATURE", 0.0),
    top_p=_env_float("LIBRARY_AGENT_TOP_P", 0.95),
    top_k=_env_int("LIBRARY_AGENT_TOP_K", None),
    max_output_tokens=_env_int("LIBRARY_AGENT_MAX_OUTPUT_TOKENS", 8192),
)

logger.info(
    "library_agent config: model=%s temperature=%s top_p=%s top_k=%s max_output_tokens=%s",
    model_name,
    generate_content_config.temperature,
    generate_content_config.top_p,
    generate_content_config.top_k,
    generate_content_config.max_output_tokens,
)


# Library/Knowledge agent
library_agent = Agent(
    model=model_name,
    name="security_training_library",
    description=(
        "Library/Knowledge agent for security training. "
        "Looks up approved modules, cadences, and policy/library content; "
        "provides policy basis and QA over the training library."
    ),
    instruction=LIBRARY_SYSTEM_INSTRUCTION,
    generate_content_config=generate_content_config,
    tools=[
        FunctionTool(load_training_library),
        FunctionTool(load_policy_texts),
        FunctionTool(search_policy_semantic),
    ],
)

# Expose as A2A app for remote_a2a_agent orchestration
a2a_app = to_a2a(library_agent, port=int(os.getenv("LIBRARY_AGENT_PORT", "9999")), host="localhost")

