-- Seed data for Loan Approval Prediction & Risk Analytics Platform

-- Insert mock users (password_hash is for 'password123', hashed with bcrypt)
-- Hashed password: $2b$12$R9h/lIPzNgb.07.zJ5N.6exqN4.v6Wn2P6V388Qe4zQ6xU3c3a.yK
INSERT INTO users (username, password_hash, is_active, role) VALUES
('admin', '$2b$12$R9h/lIPzNgb.07.zJ5N.6exqN4.v6Wn2P6V388Qe4zQ6xU3c3a.yK', TRUE, 'admin'),
('analyst', '$2b$12$R9h/lIPzNgb.07.zJ5N.6exqN4.v6Wn2P6V388Qe4zQ6xU3c3a.yK', TRUE, 'user'),
('officer', '$2b$12$R9h/lIPzNgb.07.zJ5N.6exqN4.v6Wn2P6V388Qe4zQ6xU3c3a.yK', TRUE, 'user');

-- Insert mock borrowers
INSERT INTO borrowers (user_id, gender, age, married, dependents, education, employment_type, monthly_income, coapplicant_income, loan_amount, loan_term, credit_history, existing_debt, property_area) VALUES
(1, 'Male', 35, 'Yes', 2, 'Graduate', 'Salaried', 8000.0, 2000.0, 150000.0, 360, 1.0, 5000.0, 'Urban'),
(1, 'Female', 28, 'No', 0, 'Graduate', 'Salaried', 6500.0, 0.0, 90000.0, 180, 1.0, 15000.0, 'Semiurban'),
(2, 'Male', 42, 'Yes', 3, 'Not Graduate', 'Self employed', 4500.0, 1200.0, 120000.0, 360, 0.0, 25000.0, 'Rural'),
(2, 'Female', 50, 'Yes', 1, 'Graduate', 'Salaried', 12000.0, 4000.0, 350000.0, 240, 1.0, 8000.0, 'Urban'),
(3, 'Male', 23, 'No', 0, 'Graduate', 'Self employed', 3200.0, 0.0, 60000.0, 120, 1.0, 2000.0, 'Rural');

-- Insert mock predictions
INSERT INTO predictions (borrower_id, user_id, approval_probability, approval_status, approval_threshold, risk_score, risk_category, shap_summary_path, shap_importance_path, pdf_report_path) VALUES
(1, 1, 0.885, 'approved', 0.5, 11.5, 'Low Risk', NULL, NULL, NULL),
(2, 1, 0.742, 'approved', 0.5, 25.8, 'Low Risk', NULL, NULL, NULL),
(3, 2, 0.125, 'rejected', 0.5, 87.5, 'High Risk', NULL, NULL, NULL),
(4, 2, 0.941, 'approved', 0.5, 5.9, 'Low Risk', NULL, NULL, NULL),
(5, 3, 0.620, 'approved', 0.5, 38.0, 'Medium Risk', NULL, NULL, NULL);

-- Insert mock model metrics
INSERT INTO model_metrics (model_name, accuracy, precision, recall, f1_score, roc_auc, confusion_matrix) VALUES
('LightGBM', 0.892, 0.910, 0.875, 0.892, 0.948, '[[420,41],[58,481]]'),
('XGBoost', 0.885, 0.902, 0.868, 0.885, 0.941, '[[415,46],[61,478]]'),
('RandomForest', 0.871, 0.889, 0.852, 0.870, 0.932, '[[408,53],[69,470]]'),
('LogisticRegression', 0.835, 0.842, 0.828, 0.835, 0.895, '[[389,72],[93,446]]');

-- Insert mock audit logs
INSERT INTO audit_logs (user_id, action, status, ip_address, details) VALUES
(1, 'USER_LOGIN', 'SUCCESS', '127.0.0.1', 'Admin user logged in successfully'),
(1, 'MODEL_TRAINING', 'SUCCESS', '127.0.0.1', 'Retrained all credit risk models, LightGBM selected as best (ROC-AUC=0.948)'),
(2, 'USER_LOGIN', 'SUCCESS', '127.0.0.1', 'Analyst user logged in successfully'),
(2, 'LOAN_PREDICTION', 'SUCCESS', '127.0.0.1', 'Performed prediction for Borrower ID 3: rejected (prob=0.125, risk=87.5)'),
(3, 'USER_LOGIN', 'SUCCESS', '127.0.0.1', 'Officer user logged in successfully');
