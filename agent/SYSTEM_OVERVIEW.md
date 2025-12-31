# Security Training System - Complete Component Overview

## System Architecture

This is a multi-agent security training and compliance system that uses AI agents to detect training gaps, manage assignments, and provide policy knowledge through semantic search.

---

## 🎯 Core Components

### 1. **Root Agent (devops_root)**
**Location**: `agent/devops_root/`  
**Port**: 9995  
**Model**: Gemini 3 Pro Preview

**Purpose**: Main orchestrator that routes user requests to appropriate agents

**Key Features**:
- Request routing and orchestration
- Approval workflow management
- Multi-agent coordination
- User interface entry point

**Tools**:
- `request_user_approval` - HITL approval for sensitive operations
- `awareness_agent` (Remote A2A) - Routes to Awareness Agent
- `security_training_library` (Remote A2A) - Routes to Library Agent

**Responsibilities**:
- Receives user requests via ADK Web UI
- Determines which agent should handle the request
- Manages approval workflows for destructive operations
- Coordinates between multiple agents when needed

---

### 2. **Awareness Agent (awareness_agent)**
**Location**: `agent/awareness_agent/`  
**Port**: 9998  
**Model**: Gemini 3 Pro Preview

**Purpose**: Training gap detection, assignment management, and user data operations

**Key Features**:
- Detects training gaps (overdue/missing modules)
- Creates training assignment plans
- Manages user data (CRUD operations)
- HITL approval workflow for assignments
- Integrates with Library Agent for policy lookups

**Tools**:
1. `import_user_awareness_status` - Import user data from JSON file
2. `import_user_awareness_from_upload` - Import user data from uploaded JSON content
3. `load_user_awareness_status` - Load user training status from database
4. `save_training_assignments` - Save approved assignments to database
5. `delete_user` - Delete user and all associated records
6. `request_assignment_approval` - Request HITL approval for assignments
7. `security_training_library` (Agent Tool) - Call Library Agent for policy/module info

**Database Operations**:
- **Read**: User records, training status, assignments
- **Write**: New assignments, user updates, audit logs
- **Delete**: Users and cascading records

**Workflow**:
1. Loads user data from PostgreSQL
2. Detects gaps (overdue/missing training)
3. Calls Library Agent for module details and policy citations
4. Creates assignment plan with due dates
5. Requests HITL approval
6. Saves approved assignments to database

---

### 3. **Library Agent (security_training_library)**
**Location**: `agent/library_agent/`  
**Port**: 9999  
**Model**: Gemini 3 Pro Preview

**Purpose**: Knowledge base for policies, training catalog, and semantic search

**Key Features**:
- Semantic search over policy documents
- Training catalog and rules lookup
- Policy document retrieval
- Vector-based similarity search

**Tools**:
1. `load_training_library` - Get training catalog and assignment rules (JSON)
2. `load_policy_texts` - Retrieve policy document content
3. `search_policy_semantic` - Semantic search over policy documents using vector DB

**Data Sources**:
- **ChromaDB Vector DB**: Policy documents (embeddings), training catalog, rules
- **Document Files**: Fallback to `.txt` files if vector DB unavailable

**Capabilities**:
- Answers questions like "What is our policy on X?"
- Lists mandatory training modules
- Provides policy citations (document codes, sections)
- Semantic similarity search for natural language queries

---

## 💾 Data Storage Components

### 4. **PostgreSQL Database**
**Location**: Docker container  
**Port**: 5433 (mapped from container port 5432)  
**Database**: `security_training`  
**Credentials**: postgres/postgres

**Schema**:

#### `users` Table
- Stores user information from IdP
- Fields: `user_id` (PK), `name`, `department`, `region`, `overall_status`, `last_evaluated`
- Managed by: Awareness Agent

#### `training_modules` Table
- Reference table for training modules
- Fields: `module_id` (PK), `title`, `cadence_days`, `linked_document`, `status`
- Source: Training catalog from Library Agent

#### `user_training_status` Table
- Training completion status per user
- Fields: `user_id`, `module_id`, `required`, `status`, `last_completed`, `days_overdue`, `linked_document`
- Tracks: COMPLIANT, OVERDUE, NOT_STARTED, ASSIGNED

#### `training_assignments` Table
- Assigned training with approval metadata
- Fields: `user_id`, `module_id`, `assigned_date`, `due_date`, `status`, `approver_name`, `approver_title`, `approval_date`, `approval_metadata`
- Created by: Awareness Agent after HITL approval

#### `audit_log` Table
- Compliance audit trail
- Fields: `action_type`, `user_id`, `module_id`, `approver_name`, `policy_citations`, `metadata`, `created_at`
- Tracks: ASSIGNMENT_CREATED, APPROVAL_GRANTED, STATUS_UPDATED

**Access**: Awareness Agent (read/write)

---

### 5. **ChromaDB Vector Database**
**Location**: `agent/library_agent/.chroma_db/` (local filesystem)  
**Type**: Persistent vector database

**Collections**:

#### Policy Documents
- **Document Codes**: POL-SEC-001, HR-HB-001, POL-AI-001
- **Storage**: Chunked into embeddings for semantic search
- **Metadata**: document_code, title, document_type, chunk_index, total_chunks
- **Features**: Semantic similarity search, full document reconstruction

#### TRAINING-CATALOG
- **Format**: JSON (stored as single chunk to preserve structure)
- **Content**: Training module definitions
- **Fields**: module_id, title, cadence_days, linked_document, etc.

#### TRAINING-RULES
- **Format**: JSON (stored as single chunk to preserve structure)
- **Content**: Assignment rules by department/region
- **Fields**: Rules for mandatory training per role/location

**Operations**:
- Semantic search using embeddings
- Document chunking and retrieval
- Full document reconstruction from chunks

**Access**: Library Agent (read)

---

## 📁 Supporting Files & Folders

### 6. **Document Files**
**Location**: `agent/library_agent/documents/`

**Contents**:
- Policy documents (TXT, PDF, DOCX formats)
  - `Information_Security_Policy.txt`
  - `Human_Resources_Employee_Handbook.txt`
  - `AI_and_Automated_Decision_Making_Policy.txt`
- Training data
  - `training_catalog.txt` (JSON format)
  - `training_rules.txt` (JSON format)

**Purpose**: Source files for indexing into ChromaDB, fallback if vector DB unavailable

---

### 7. **Database Initialization**
**Location**: `agent/awareness_agent/init_db.sql`

**Purpose**: SQL schema definition for PostgreSQL
- Creates all tables with proper relationships
- Sets up indexes for performance
- Defines CASCADE constraints for data integrity

**Usage**: Run once when setting up the database

---

### 8. **Docker Configuration**
**Location**: `agent/awareness_agent/docker-compose.yml`

**Purpose**: PostgreSQL container setup
- Defines database service
- Sets environment variables (user, password, database name)
- Maps port 5433 (host) to 5432 (container)
- Health check configuration

**Usage**: `docker-compose up -d` to start database

---

## 🔄 Data Flow Examples

### Example 1: Gap Detection with Policy Citations
```
User → Root Agent → Awareness Agent
                      │
                      ├─→ PostgreSQL: Load users
                      │
                      ├─→ Detect gaps
                      │
                      └─→ Library Agent (A2A)
                            │
                            ├─→ ChromaDB: Get catalog
                            ├─→ ChromaDB: Get policy citations
                            └─→ Return module details
                      │
                      ├─→ Create assignment plan
                      ├─→ Request HITL approval
                      └─→ PostgreSQL: Save assignments
```

### Example 2: Policy Query
```
User → Root Agent → Library Agent
                      │
                      ├─→ ChromaDB: Semantic search
                      ├─→ ChromaDB: Retrieve policy text
                      └─→ Return with citations
```

### Example 3: User Deletion
```
User → Root Agent → Awareness Agent
                      │
                      ├─→ PostgreSQL: Delete user
                      ├─→ PostgreSQL: Cascade delete training_status
                      ├─→ PostgreSQL: Cascade delete assignments
                      └─→ PostgreSQL: Delete audit_log entries
```

---

## 🛠️ Technology Stack

### AI/ML
- **Framework**: Google ADK (Agent Development Kit)
- **Model**: Gemini 3 Pro Preview
- **Protocol**: A2A (Agent-to-Agent) over HTTP

### Databases
- **PostgreSQL**: Relational database (Docker)
- **ChromaDB**: Vector database (local filesystem)
- **ORM**: psycopg2 (PostgreSQL), ChromaDB Python client

### Infrastructure
- **Container**: Docker (PostgreSQL)
- **Ports**: 
  - 9995 (Root Agent)
  - 9998 (Awareness Agent)
  - 9999 (Library Agent)
  - 5433 (PostgreSQL)

### File Formats
- **JSON**: Training catalog, rules, user data
- **TXT**: Policy documents (extracted from PDF/DOCX)
- **PDF/DOCX**: Original policy documents

---

## 📊 Component Interactions

### Agent-to-Agent Communication
- **Protocol**: A2A (Agent-to-Agent) over HTTP
- **Root → Awareness**: Direct routing
- **Root → Library**: Direct routing
- **Awareness → Library**: Internal A2A call for policy lookups

### Database Access
- **Awareness Agent → PostgreSQL**: Direct SQL via psycopg2
- **Library Agent → ChromaDB**: ChromaDB Python client

### Data Import/Export
- **JSON Import**: User awareness status via Awareness Agent
- **Database Export**: Query via Awareness Agent tools
- **Vector DB Indexing**: Manual via indexing scripts (if needed)

---

## 🎯 Use Cases

### 1. Training Gap Detection
- **Trigger**: "Which users need AI training?"
- **Agents**: Root → Awareness → Library
- **Output**: List of users with gaps, proposed assignments, policy citations

### 2. Policy Query
- **Trigger**: "What is our policy on remote work?"
- **Agents**: Root → Library
- **Output**: Policy text with document code and section citations

### 3. User Management
- **Trigger**: "Delete user jake"
- **Agents**: Root → Awareness
- **Output**: User and all associated records deleted

### 4. Data Import
- **Trigger**: Paste JSON user data
- **Agents**: Root → Awareness
- **Output**: Users imported into database

---

## 🔐 Security & Compliance

### Audit Trail
- All assignments logged in `audit_log` table
- Includes: approver info, policy citations, timestamps
- Immutable record for compliance

### Approval Workflow
- HITL (Human-In-The-Loop) for all assignments
- Approval metadata stored with assignments
- Prevents unauthorized training assignments

### Data Integrity
- Foreign key constraints in PostgreSQL
- CASCADE deletes for data consistency
- Transaction-based operations

---

## 📝 Key Files Reference

### Agent Files
- `agent/devops_root/agent.py` - Root agent definition
- `agent/awareness_agent/agent.py` - Awareness agent definition
- `agent/library_agent/agent.py` - Library agent definition

### Database Files
- `agent/awareness_agent/db_utils.py` - PostgreSQL utilities
- `agent/awareness_agent/init_db.sql` - Database schema
- `agent/awareness_agent/docker-compose.yml` - Database container

### Vector DB Files
- `agent/library_agent/vector_db.py` - ChromaDB utilities
- `agent/library_agent/.chroma_db/` - Vector database storage

### Configuration
- `agent/.env` - Environment variables (model names, ports, DB config)

---

## 🚀 Quick Start

1. **Start PostgreSQL**: `cd agent/awareness_agent && docker-compose up -d`
2. **Start Library Agent**: `cd agent/library_agent && python -m library_agent`
3. **Start Awareness Agent**: `cd agent/awareness_agent && python -m awareness_agent`
4. **Start Root Agent**: `cd agent/devops_root && python -m devops_root`
5. **Access**: Open ADK Web UI and connect to Root Agent (port 9995)

---

## 📈 System Capabilities

✅ **Gap Detection**: Automatically identifies overdue/missing training  
✅ **Policy Search**: Semantic search over policy documents  
✅ **Assignment Management**: Creates and tracks training assignments  
✅ **HITL Approval**: Human approval workflow for compliance  
✅ **Audit Trail**: Complete compliance logging  
✅ **User Management**: Full CRUD operations on user data  
✅ **Multi-Agent Coordination**: Seamless agent-to-agent communication  
✅ **Vector Search**: Fast semantic similarity search  

---

This system provides a complete solution for security training management with AI-powered gap detection, policy knowledge base, and compliance tracking.

