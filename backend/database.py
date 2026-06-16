import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Load environmental variables
load_dotenv()


def get_db_url() -> str:
    """Determine the database connection URL.

    Checks:
      1. DATABASE_URL env var (converts postgres:// to postgresql:// if needed)
      2. DB_* env vars to construct a PostgreSQL URL
      3. Fallback to local SQLite file
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url

    # Check individual PostgreSQL variables
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    if db_user and db_password and db_host and db_name:
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Standard SQLite fallback for local testing & development portability
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sqlite_path = os.path.join(project_root, "loan_risk.db")
    return f"sqlite:///{sqlite_path}"


def get_engine():
    url = get_db_url()
    connect_args = {}
    if url.startswith("sqlite"):
        # SQLite-specific pool configuration
        connect_args = {"check_same_thread": False}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency injector for FastAPI DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
