import sqlite3
from pathlib import Path
import sys


def init_db():
    project_root = Path(__file__).resolve().parents[2]
    sql_file = project_root / "resources" / "init.sql"
    db_file = project_root / "feeminton.db"

    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")

    conn = sqlite3.connect(str(db_file))
    try:
        cursor = conn.cursor()
        sql_script = sql_file.read_text(encoding="utf-8")
        cursor.executescript(sql_script)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        init_db()
        print("Database initialized!")
    except Exception as e:
        print(f"Failed to initialize database: {e}", file=sys.stderr)
        sys.exit(1)
