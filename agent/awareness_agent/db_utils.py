"""Database utilities for security training awareness status."""
import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger(__name__)

# Database connection pool
_pool: Optional[SimpleConnectionPool] = None


def get_db_pool():
    """Get or create database connection pool."""
    global _pool
    if _pool is None:
        db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5433")),  # Changed to 5433 to avoid local PostgreSQL conflict
            "database": os.getenv("DB_NAME", "security_training"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
        }
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **db_config
        )
        logger.info("Created database connection pool: %s@%s:%s/%s", 
                   db_config["user"], db_config["host"], db_config["port"], db_config["database"])
    return _pool


def get_db_connection():
    """Get a connection from the pool."""
    pool = get_db_pool()
    return pool.getconn()


def return_db_connection(conn):
    """Return a connection to the pool."""
    pool = get_db_pool()
    pool.putconn(conn)


def _extract_json_from_text(text: str) -> str:
    """Extract JSON from text that might contain markdown code blocks or extra text.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Extracted JSON string
    """
    # First, try to extract JSON from markdown code blocks
    json_pattern = r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Try to find JSON by looking for balanced brackets
    # Find the first [ or { and try to extract balanced JSON
    text_stripped = text.strip()
    
    # Try array first (most common for user data)
    start_idx = text_stripped.find('[')
    if start_idx != -1:
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_idx, len(text_stripped)):
            char = text_stripped[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        # Found balanced array
                        json_candidate = text_stripped[start_idx:i+1]
                        try:
                            # Validate it's valid JSON
                            json.loads(json_candidate)
                            return json_candidate
                        except json.JSONDecodeError:
                            pass
    
    # Try object
    start_idx = text_stripped.find('{')
    if start_idx != -1:
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_idx, len(text_stripped)):
            char = text_stripped[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        # Found balanced object
                        json_candidate = text_stripped[start_idx:i+1]
                        try:
                            # Validate it's valid JSON
                            json.loads(json_candidate)
                            return json_candidate
                        except json.JSONDecodeError:
                            pass
    
    # If no pattern found, return the original text (might be pure JSON)
    return text_stripped


def import_user_awareness_from_json_content(json_content: str) -> dict:
    """Import user awareness status from JSON content string into database.
    
    Args:
        json_content: JSON string containing user awareness status data.
                     Can be pure JSON, JSON in markdown code blocks, or JSON embedded in text.
        
    Returns:
        Dictionary with import results (users_imported, status_updated, errors)
    """
    logger.info("Importing user awareness status from JSON content")
    
    # Extract JSON from text (handles markdown code blocks, extra text, etc.)
    try:
        extracted_json = _extract_json_from_text(json_content)
        users_data = json.loads(extracted_json)
    except json.JSONDecodeError as e:
        logger.exception("Failed to parse JSON content: %s", e)
        logger.error("JSON content (first 500 chars): %s", json_content[:500])
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            users_imported = 0
            status_updated = 0
            errors = []
            
            for user_data in users_data:
                user_id = user_data.get("user_id")
                if not user_id:
                    errors.append(f"Missing user_id in record: {user_data.get('name', 'unknown')}")
                    continue
                
                try:
                    # Upsert user
                    cur.execute("""
                        INSERT INTO users (user_id, name, department, region, overall_status, last_evaluated, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            department = EXCLUDED.department,
                            region = EXCLUDED.region,
                            overall_status = EXCLUDED.overall_status,
                            last_evaluated = EXCLUDED.last_evaluated,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        user_id,
                        user_data.get("name"),
                        user_data.get("department"),
                        user_data.get("region"),
                        user_data.get("overall_status", "UNKNOWN"),
                        user_data.get("last_evaluated"),
                    ))
                    users_imported += 1
                    
                    # Delete old training status for this user
                    cur.execute("DELETE FROM user_training_status WHERE user_id = %s", (user_id,))
                    
                    # Insert training status records
                    training_status = user_data.get("training_status", [])
                    if training_status:
                        status_records = []
                        for ts in training_status:
                            status_records.append((
                                user_id,
                                ts.get("module_id"),
                                ts.get("required", True),
                                ts.get("status"),
                                ts.get("last_completed"),
                                ts.get("days_overdue", 0),
                                ts.get("linked_document"),
                            ))
                        
                        execute_values(
                            cur,
                            """
                            INSERT INTO user_training_status 
                            (user_id, module_id, required, status, last_completed, days_overdue, linked_document)
                            VALUES %s
                            ON CONFLICT (user_id, module_id) DO UPDATE SET
                                required = EXCLUDED.required,
                                status = EXCLUDED.status,
                                last_completed = EXCLUDED.last_completed,
                                days_overdue = EXCLUDED.days_overdue,
                                linked_document = EXCLUDED.linked_document,
                                updated_at = CURRENT_TIMESTAMP
                            """,
                            status_records,
                            template=None
                        )
                        status_updated += len(status_records)
                    
                except Exception as e:
                    logger.exception("Failed to import user %s: %s", user_id, e)
                    errors.append(f"User {user_id}: {str(e)}")
            
            conn.commit()
            logger.info("Imported %d users, updated %d training status records", 
                       users_imported, status_updated)
            
            return {
                "success": True,
                "users_imported": users_imported,
                "status_updated": status_updated,
                "errors": errors if errors else None,
            }
            
    except Exception as e:
        conn.rollback()
        logger.exception("Failed to import user awareness status: %s", e)
        return {"success": False, "error": str(e)}
    finally:
        return_db_connection(conn)


def import_user_awareness_from_json(json_file_path: str) -> dict:
    """Import user awareness status from JSON file into database.
    
    Args:
        json_file_path: Path to JSON file with user awareness status
        
    Returns:
        Dictionary with import results (users_imported, status_updated, errors)
    """
    logger.info("Importing user awareness status from %s", json_file_path)
    
    json_path = Path(json_file_path)
    if not json_path.exists():
        return {"success": False, "error": f"File not found: {json_file_path}"}
    
    try:
        with json_path.open("r", encoding="utf-8") as f:
            users_data = json.loads(f.read())
    except Exception as e:
        logger.exception("Failed to read JSON file: %s", e)
        return {"success": False, "error": str(e)}
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            users_imported = 0
            status_updated = 0
            errors = []
            
            for user_data in users_data:
                user_id = user_data.get("user_id")
                if not user_id:
                    errors.append(f"Missing user_id in record: {user_data.get('name', 'unknown')}")
                    continue
                
                try:
                    # Upsert user
                    cur.execute("""
                        INSERT INTO users (user_id, name, department, region, overall_status, last_evaluated, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            department = EXCLUDED.department,
                            region = EXCLUDED.region,
                            overall_status = EXCLUDED.overall_status,
                            last_evaluated = EXCLUDED.last_evaluated,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        user_id,
                        user_data.get("name"),
                        user_data.get("department"),
                        user_data.get("region"),
                        user_data.get("overall_status", "UNKNOWN"),
                        user_data.get("last_evaluated"),
                    ))
                    users_imported += 1
                    
                    # Delete old training status for this user
                    cur.execute("DELETE FROM user_training_status WHERE user_id = %s", (user_id,))
                    
                    # Insert training status records
                    training_status = user_data.get("training_status", [])
                    if training_status:
                        status_records = []
                        for ts in training_status:
                            status_records.append((
                                user_id,
                                ts.get("module_id"),
                                ts.get("required", True),
                                ts.get("status"),
                                ts.get("last_completed"),
                                ts.get("days_overdue", 0),
                                ts.get("linked_document"),
                            ))
                        
                        execute_values(
                            cur,
                            """
                            INSERT INTO user_training_status 
                            (user_id, module_id, required, status, last_completed, days_overdue, linked_document)
                            VALUES %s
                            ON CONFLICT (user_id, module_id) DO UPDATE SET
                                required = EXCLUDED.required,
                                status = EXCLUDED.status,
                                last_completed = EXCLUDED.last_completed,
                                days_overdue = EXCLUDED.days_overdue,
                                linked_document = EXCLUDED.linked_document,
                                updated_at = CURRENT_TIMESTAMP
                            """,
                            status_records,
                            template=None
                        )
                        status_updated += len(status_records)
                    
                except Exception as e:
                    logger.exception("Failed to import user %s: %s", user_id, e)
                    errors.append(f"User {user_id}: {str(e)}")
            
            conn.commit()
            logger.info("Imported %d users, updated %d training status records", 
                       users_imported, status_updated)
            
            return {
                "success": True,
                "users_imported": users_imported,
                "status_updated": status_updated,
                "errors": errors if errors else None,
            }
            
    except Exception as e:
        conn.rollback()
        logger.exception("Failed to import user awareness status: %s", e)
        return {"success": False, "error": str(e)}
    finally:
        return_db_connection(conn)


def load_user_awareness_status_from_db() -> dict:
    """Load user awareness status from database.
    
    Returns:
        Dictionary with 'users' list containing user training status records.
    """
    logger.info("Loading user awareness status from database")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all users with their training status
            cur.execute("""
                SELECT 
                    u.user_id,
                    u.name,
                    u.department,
                    u.region,
                    u.overall_status,
                    u.last_evaluated,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'module_id', ts.module_id,
                                'title', tm.title,
                                'required', ts.required,
                                'status', ts.status,
                                'last_completed', ts.last_completed,
                                'days_overdue', ts.days_overdue,
                                'linked_document', ts.linked_document
                            )
                        ) FILTER (WHERE ts.module_id IS NOT NULL),
                        '[]'::json
                    ) as training_status
                FROM users u
                LEFT JOIN user_training_status ts ON u.user_id = ts.user_id
                LEFT JOIN training_modules tm ON ts.module_id = tm.module_id
                GROUP BY u.user_id, u.name, u.department, u.region, u.overall_status, u.last_evaluated
                ORDER BY u.user_id
            """)
            
            rows = cur.fetchall()
            users = []
            for row in rows:
                user = dict(row)
                # Convert training_status from JSON to list
                if isinstance(user.get("training_status"), str):
                    user["training_status"] = json.loads(user["training_status"])
                elif user.get("training_status") is None:
                    user["training_status"] = []
                users.append(user)
            
            logger.info("Loaded %d user records from database", len(users))
            return {"users": users, "loaded_at": datetime.now().isoformat()}
            
    except Exception as e:
        logger.exception("Failed to load user awareness status: %s", e)
        return {"users": [], "error": str(e)}
    finally:
        return_db_connection(conn)


def save_training_assignments_to_db(
    assignments: List[Dict[str, Any]],
    approver_name: Optional[str] = None,
    approver_title: Optional[str] = None,
    approval_date: Optional[str] = None,
) -> dict:
    """Save approved training assignments to database.
    
    Args:
        assignments: List of assignment dicts
        approver_name: Name of approver
        approver_title: Title of approver
        approval_date: Approval date in ISO format
        
    Returns:
        Dictionary with success status and updated record count.
    """
    logger.info("Saving %d training assignments to database", len(assignments))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            updated_count = 0
            approval_meta = {
                "approver_name": approver_name,
                "approver_title": approver_title,
                "approval_date": approval_date or datetime.now().isoformat(),
            }
            
            for assignment in assignments:
                user_id = assignment.get("user_id")
                module_id = assignment.get("module_id")
                
                if not user_id or not module_id:
                    continue
                
                # Insert assignment
                cur.execute("""
                    INSERT INTO training_assignments 
                    (user_id, module_id, assigned_date, due_date, status, approver_name, approver_title, approval_date, approval_metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    user_id,
                    module_id,
                    assignment.get("assigned_date", datetime.now().isoformat()),
                    assignment.get("due_date"),
                    "ASSIGNED",
                    approver_name,
                    approver_title,
                    approval_date or datetime.now(),
                    json.dumps(approval_meta),
                ))
                
                # Update user_training_status
                cur.execute("""
                    INSERT INTO user_training_status 
                    (user_id, module_id, required, status, linked_document, updated_at)
                    VALUES (%s, %s, TRUE, 'ASSIGNED', %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id, module_id) DO UPDATE SET
                        status = 'ASSIGNED',
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_id,
                    module_id,
                    assignment.get("linked_document"),
                ))
                
                # Update user overall_status if needed
                cur.execute("""
                    UPDATE users 
                    SET overall_status = 'NON_COMPLIANT', 
                        last_evaluated = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND overall_status = 'COMPLIANT'
                """, (user_id,))
                
                # Create audit log entry
                cur.execute("""
                    INSERT INTO audit_log 
                    (action_type, user_id, module_id, approver_name, approver_title, policy_citations, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    "ASSIGNMENT_CREATED",
                    user_id,
                    module_id,
                    approver_name,
                    approver_title,
                    json.dumps(assignment.get("policy_citations", [])),
                    json.dumps(approval_meta),
                ))
                
                updated_count += 1
            
            conn.commit()
            logger.info("Saved %d assignments to database", updated_count)
            
            return {
                "success": True,
                "updated_users": updated_count,
                "approval_metadata": approval_meta,
            }
            
    except Exception as e:
        conn.rollback()
        logger.exception("Failed to save training assignments: %s", e)
        return {"success": False, "error": str(e)}
    finally:
        return_db_connection(conn)


def delete_user_from_db(user_id: str) -> dict:
    """Delete a user and all associated records from the database.
    
    This will delete:
    - The user record from the users table
    - All training status records (via CASCADE)
    - All training assignments (via CASCADE)
    - All audit log entries for this user
    
    Args:
        user_id: The user_id of the user to delete
        
    Returns:
        Dictionary with success status and deletion details.
    """
    logger.info("Deleting user %s from database", user_id)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # First, check if user exists
            cur.execute("SELECT user_id, name FROM users WHERE user_id = %s", (user_id,))
            user_record = cur.fetchone()
            
            if not user_record:
                return {
                    "success": False,
                    "error": f"User {user_id} not found in database",
                }
            
            user_name = user_record[1]
            
            # Count related records before deletion (for reporting)
            cur.execute("SELECT COUNT(*) FROM user_training_status WHERE user_id = %s", (user_id,))
            training_status_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM training_assignments WHERE user_id = %s", (user_id,))
            assignments_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM audit_log WHERE user_id = %s", (user_id,))
            audit_log_count = cur.fetchone()[0]
            
            # Delete audit log entries (no CASCADE, so manual deletion)
            cur.execute("DELETE FROM audit_log WHERE user_id = %s", (user_id,))
            
            # Delete user (this will CASCADE to user_training_status and training_assignments)
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            
            conn.commit()
            
            logger.info(
                "Deleted user %s (%s): %d training status records, %d assignments, %d audit log entries",
                user_id, user_name, training_status_count, assignments_count, audit_log_count
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "user_name": user_name,
                "deleted_records": {
                    "training_status": training_status_count,
                    "assignments": assignments_count,
                    "audit_log": audit_log_count,
                },
            }
            
    except Exception as e:
        conn.rollback()
        logger.exception("Failed to delete user %s: %s", user_id, e)
        return {"success": False, "error": str(e)}
    finally:
        return_db_connection(conn)

