@echo off
title Loan Risk Assessment Platform Startup
echo ==========================================================
echo       LOAN RISK ASSESSMENT PLATFORM STARTUP SCRIPT
echo ==========================================================
echo.

:: Check for virtual environment
if not exist venv (
    echo [ERROR] Virtual environment 'venv' not found.
    echo Please run: python -m venv venv and pip install -r requirements.txt
    pause
    exit /b 1
)

:: Activate environment
echo [1/4] Activating Python Virtual Environment...
call venv\Scripts\activate.bat
echo.

:: Seed database
echo [2/4] Initializing and Seeding Local Database...
set DATABASE_URL=sqlite:///loan_risk.db
python backend/scripts/seed_db.py
if %errorlevel% neq 0 (
    echo [ERROR] Seeding database failed.
    pause
    exit /b 1
)
echo.

:: Train model weights
echo [3/4] Running ML Model Training Pipeline (LightGBM/XGB/RF/LR)...
python train_model.py
if %errorlevel% neq 0 (
    echo [ERROR] Model training failed.
    pause
    exit /b 1
)
echo.

:: Start server
echo [4/4] Launching FastAPI ASGI Server (React SPA + APIs)...
echo ----------------------------------------------------------
echo  Application is live at: http://127.0.0.1:5000/
echo  Interactive Swagger docs: http://127.0.0.1:5000/docs
echo ----------------------------------------------------------
echo.
python -m uvicorn backend.app:app --host 127.0.0.1 --port 5000

pause
