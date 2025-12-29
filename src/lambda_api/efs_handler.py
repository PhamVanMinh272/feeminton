import datetime
import json
import os
import boto3

from src.common.db_connection import connect_db, initialize_db
from src.settings import SQLITE_PATH, DDL_PATH, DML_PATH, logger


def run_ddl():
    """Run DDL script to create tables in the SQLite database."""
    logger.info("Running DDL script ...")
    conn = connect_db(SQLITE_PATH)
    cursor = conn.cursor()

    with open(DDL_PATH, "r", encoding='utf-8') as file:
        ddl_script = file.read()
    cursor.executescript(ddl_script)
    conn.commit()
    conn.close()


def run_dml():
    """
    Run DML script to insert initial data into the SQLite database.
    Make sure to put unique constraints to avoid duplication.
    """
    logger.info("Running DML script ...")
    conn = connect_db(SQLITE_PATH)
    cursor = conn.cursor()

    with open(DML_PATH, encoding="utf-8", errors="replace") as file:
        dml_script = file.read()
        logger.info("Loaded sql script")
    cursor.executescript(dml_script)
    conn.commit()
    conn.close()


def remove_db_file():
    """Remove the SQLite database file."""
    logger.info("Removing DB file ...")
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
        logger.info(f"Removed database file at: {SQLITE_PATH}")
    else:
        logger.info("Database file does not exist, nothing to remove.")


def push_to_s3():
    logger.info("Pushing to S3 ...")
    s3 = boto3.client("s3")
    bucket_name = "badminton-recharging-website"
    s3_key = "bmt_recharging.db"
    file_path = "/mnt/efs/bmt_recharging.db"
    logger.info(f"Checking file at path: {file_path}")

    if os.path.exists(file_path):
        logger.info(f"File Name: {os.path.basename(file_path)}")
        logger.info(f"Directory: {os.path.dirname(file_path)}")
        logger.info(f"Absolute Path: {os.path.abspath(file_path)}")
        logger.info(f"File Size (bytes): {os.path.getsize(file_path)}")

        # Get creation and modification times as timestamps
        creation_timestamp = os.path.getctime(file_path)
        modification_timestamp = os.path.getmtime(file_path)

        # Convert timestamps to human-readable datetime objects
        creation_time = datetime.datetime.fromtimestamp(creation_timestamp)
        modification_time = datetime.datetime.fromtimestamp(modification_timestamp)

        logger.info(f"Creation Time: {creation_time}")
        logger.info(f"Modification Time: {modification_time}")
    else:
        logger.info(f"Error: File not found at '{file_path}'")

    try:
        # with open(local_path, 'rb') as f:
        s3.upload_file(file_path, bucket_name, s3_key)
        return {
            "statusCode": 200,
            "body": f"Successfully uploaded to s3://{bucket_name}/{s3_key}",
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}


def init_db():
    logger.info("Initializing DB ...")
    remove_db_file()
    initialize_db()
    run_ddl()
    run_dml()
    return {"statusCode": 200, "body": json.dumps("Initialized DB")}


db_strategies = {
    "remove_db_file": remove_db_file,
    "init_db": init_db,
    "run_ddl": run_ddl,
    "run_dml": run_dml,
    "push_to_s3": push_to_s3,
}


def get_help():
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "task_type field required with available value: "
                + ", ".join(db_strategies.keys())
            }
        ),
    }


def lambda_handler(event, context):
    # Example: Read from SQLite (mounted via EFS at /mnt/sqlite/bmt_recharging.db)
    try:
        task_type = event.get("task_type", "")
        if not task_type or task_type not in db_strategies:
            return get_help()
        result = db_strategies[task_type]()
        logger.info("Result: " + str(result))
        return {"statusCode": 200, "body": json.dumps("Done " + task_type)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


if __name__ == "__main__":
    # Test event
    test_event = {"task_type": "init_db"}
    print(lambda_handler(test_event, None))
