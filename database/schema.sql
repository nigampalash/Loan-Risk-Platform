-- PostgreSQL schema for Loan Approval Prediction & Risk Analytics Platform

-- Drop tables if they exist
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS model_metrics CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS borrowers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users Table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  role VARCHAR(50) NOT NULL DEFAULT 'user',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Borrowers Table (Applicant features)
CREATE TABLE borrowers (
  id SERIAL PRIMARY KEY,
  user_id INT NULL REFERENCES users(id) ON DELETE SET NULL,
  gender VARCHAR(20) NOT NULL,
  age INT NOT NULL,
  married VARCHAR(10) NOT NULL,
  dependents INT NOT NULL,
  education VARCHAR(50) NOT NULL,
  employment_type VARCHAR(50) NOT NULL,
  monthly_income DOUBLE PRECISION NOT NULL,
  coapplicant_income DOUBLE PRECISION NOT NULL,
  loan_amount DOUBLE PRECISION NOT NULL,
  loan_term INT NOT NULL,
  credit_history DOUBLE PRECISION NOT NULL,
  existing_debt DOUBLE PRECISION NOT NULL,
  property_area VARCHAR(50) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Predictions Table
CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  borrower_id INT NOT NULL REFERENCES borrowers(id) ON DELETE CASCADE,
  user_id INT NULL REFERENCES users(id) ON DELETE SET NULL,
  approval_probability DOUBLE PRECISION NOT NULL,
  approval_status VARCHAR(20) NOT NULL,
  approval_threshold DOUBLE PRECISION NOT NULL,
  risk_score DOUBLE PRECISION NOT NULL,
  risk_category VARCHAR(50) NOT NULL,
  shap_summary_path VARCHAR(500) NULL,
  shap_importance_path VARCHAR(500) NULL,
  pdf_report_path VARCHAR(500) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Model Metrics Table
CREATE TABLE model_metrics (
  id SERIAL PRIMARY KEY,
  model_name VARCHAR(100) NOT NULL,
  accuracy DOUBLE PRECISION NOT NULL,
  precision DOUBLE PRECISION NOT NULL,
  recall DOUBLE PRECISION NOT NULL,
  f1_score DOUBLE PRECISION NOT NULL,
  roc_auc DOUBLE PRECISION NOT NULL,
  confusion_matrix TEXT NOT NULL, -- JSON formatted array
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs Table
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INT NULL REFERENCES users(id) ON DELETE SET NULL,
  action VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL,
  ip_address VARCHAR(45) NULL,
  details TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for query optimization
CREATE INDEX idx_borrowers_user ON borrowers(user_id);
CREATE INDEX idx_predictions_borrower ON predictions(borrower_id);
CREATE INDEX idx_predictions_user ON predictions(user_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
