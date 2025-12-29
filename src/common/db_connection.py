import os
import sqlite3
from src.settings import SQLITE_PATH, logger


def connect_db(db_path: str = SQLITE_PATH):
    logger.info(f"Attempting to connect to database at: {db_path}")
    if not os.path.exists(db_path):
        raise FileNotFoundError("Database file not found!")

    conn = sqlite3.connect(db_path)
    logger.info("Connected to the database successfully.")
    return conn


def initialize_db(db_path: str = SQLITE_PATH):
    """Initialize the SQLite database."""
    if os.path.exists(db_path):
        logger.info(f"Database already exists at: {db_path}")
        return
    else:
        logger.info(f"Creating new database at: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.close()
        logger.info("Database created successfully.")


def db_context_manager(func):
    def wrapper(*args, **kwargs):
        conn = connect_db()
        try:
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            conn.rollback()  # Important to release the lock
            raise e
        finally:
            conn.close()
            logger.info("Closing database connection.")

    return wrapper
