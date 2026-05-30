import os
import sys
from dotenv import load_dotenv

# Ensure package imports work when running this script directly.
# Adds project root to sys.path so `import backend...` succeeds.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import get_engine



def main():
    load_dotenv()

    # If DB is unreachable, skip init so the rest of the app (ML/Frontend) can run.
    # DB-backed features (analytics persistence, auth storage) may be disabled.
    try:
        engine = get_engine()
    except Exception as e:
        print(f"Failed to create DB engine: {e}")
        return
    sql_path = os.path.join(os.path.dirname(__file__), "..", "..", "database", "schema.sql")
    sql_path = os.path.abspath(sql_path)

    with open(sql_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Split on semicolons for simple execution (safe for our generated schema)
    statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(  # type: ignore[attr-defined]
                # SQLAlchemy 2.0 uses text() under the hood via conn.exec_driver_sql
                # but conn.execute with raw string may be accepted in practice.
                # To be safe across versions, use exec_driver_sql.
                #
                # We'll execute via driver sql.
                #
                # pyright/pylance: conn.execute accepts TextClause or executable.
                # We'll use exec_driver_sql for broad compatibility.
                conn.exec_driver_sql(stmt)
            )


if __name__ == "__main__":
    main()

