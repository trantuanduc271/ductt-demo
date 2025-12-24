-- Security Training Database Schema

-- Users table (from IdP attributes)
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    region VARCHAR(50),
    overall_status VARCHAR(50) DEFAULT 'UNKNOWN',
    last_evaluated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training modules reference (from catalog)
CREATE TABLE IF NOT EXISTS training_modules (
    module_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    cadence_days INTEGER DEFAULT 365,
    linked_document VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Approved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User training status (from LMS/dashboard signals)
CREATE TABLE IF NOT EXISTS user_training_status (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    module_id VARCHAR(50) NOT NULL,
    required BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) NOT NULL, -- COMPLIANT, OVERDUE, NOT_STARTED, ASSIGNED
    last_completed DATE,
    days_overdue INTEGER DEFAULT 0,
    linked_document VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, module_id)
);

-- Training assignments (created by Awareness Agent)
CREATE TABLE IF NOT EXISTS training_assignments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    module_id VARCHAR(50) NOT NULL,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'ASSIGNED', -- ASSIGNED, COMPLETED, OVERDUE, CANCELLED
    approver_name VARCHAR(255),
    approver_title VARCHAR(255),
    approval_date TIMESTAMP,
    approval_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for compliance
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(100) NOT NULL, -- ASSIGNMENT_CREATED, APPROVAL_GRANTED, STATUS_UPDATED
    user_id VARCHAR(50),
    module_id VARCHAR(50),
    approver_name VARCHAR(255),
    approver_title VARCHAR(255),
    policy_citations JSONB, -- Array of {document_code, section, reason}
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_training_status_user_id ON user_training_status(user_id);
CREATE INDEX IF NOT EXISTS idx_user_training_status_module_id ON user_training_status(module_id);
CREATE INDEX IF NOT EXISTS idx_training_assignments_user_id ON training_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_training_assignments_due_date ON training_assignments(due_date);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

