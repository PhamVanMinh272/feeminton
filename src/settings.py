import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ENV = os.environ.get("ENV", "local")

# DB
SQLITE_PATH = "/mnt/efs/feeminton.db"
DDL_PATH = os.path.join("/var/task", "resources", "ddl.sql")
DML_PATH = os.path.join("/var/task", "resources", "dml.sql")
if ENV == "local":
    if not os.path.exists(SQLITE_PATH):
        logger.info("Running in Flask local environment")
        SQLITE_PATH = "resources/feeminton.db"
        DDL_PATH = os.path.join("../resources", "ddl.sql")
        DML_PATH = os.path.join("../resources", "dml.sql")

    if not os.path.exists(SQLITE_PATH):
        # # run aws lambda in local
        # someone set working directory to feeminton/src/lambda_api
        logger.info("Running in lambda local environment")
        SQLITE_PATH = os.path.join(os.pardir, os.pardir, "resources", "feeminton.db")
        DDL_PATH = os.path.join(os.pardir, os.pardir, "resources", "ddl.sql")
        DML_PATH = os.path.join(os.pardir, os.pardir, "resources", "dml.sql")
