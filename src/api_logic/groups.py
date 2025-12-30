from src.settings import logger
from src.services.groups import GroupService
from src.common.db_connection import db_context_manager

@db_context_manager
def get_groups(conn, **kwargs):
    data = GroupService(conn).get_groups()
    logger.info(f"Fetched members: {data}")
    return {"data": data}