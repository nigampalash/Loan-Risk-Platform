import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def _get_env(name: str, default: str | None = None) -> str:
    load_dotenv()
    v = os.getenv(name)
    if v is None:
        if default is None:
            raise RuntimeError(f"Missing environment variable: {name}")
        return default
    return v


def get_engine():
    # Default to localhost for non-docker/dev runs.
    host = _get_env("MYSQL_HOST", "127.0.0.1")
    port = int(_get_env("MYSQL_PORT", "3306"))
    user = _get_env("MYSQL_USER", "root")
    password = _get_env("MYSQL_PASSWORD", "rootpassword")
    db = _get_env("MYSQL_DB", "loananalytics")

    # Use mysqlclient if available; fallback to pymysql driver.
    # SQLAlchemy URL:
    # mysql+pymysql://user:pass@host:port/db
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
    return create_engine(url, pool_pre_ping=True)

