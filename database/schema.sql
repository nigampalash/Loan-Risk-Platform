-- MySQL schema for Loan Approval Prediction & Risk Analytics Platform

CREATE DATABASE IF NOT EXISTS loananalytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE loananalytics;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_applications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  applicant_json VARCHAR(10000) NOT NULL,
  loan_amount DOUBLE NULL,
  loan_term INT NULL,
  credit_history DOUBLE NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_loan_app_user (user_id),
  CONSTRAINT fk_loan_app_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  loan_application_id INT NOT NULL,
  approval_probability DOUBLE NOT NULL,
  approval_status VARCHAR(10) NOT NULL,
  model_name VARCHAR(100) NOT NULL,
  approval_threshold DOUBLE NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_pred_loan_app (loan_application_id),
  CONSTRAINT fk_pred_loan_app
    FOREIGN KEY (loan_application_id) REFERENCES loan_applications(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS risk_scores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prediction_id INT NOT NULL,
  risk_score DOUBLE NOT NULL,
  risk_category VARCHAR(20) NOT NULL,
  shap_summary_path VARCHAR(500) NULL,
  shap_importance_path VARCHAR(500) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_risk_pred (prediction_id),
  CONSTRAINT fk_risk_pred
    FOREIGN KEY (prediction_id) REFERENCES predictions(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  level VARCHAR(20) NOT NULL DEFAULT 'INFO',
  message VARCHAR(10000) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_logs_user (user_id),
  CONSTRAINT fk_logs_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE SET NULL
);

