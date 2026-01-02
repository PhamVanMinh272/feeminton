from src.settings import logger
from src.services.groups import GroupService
from src.common.db_connection import db_context_manager


@db_context_manager
def get_groups(conn, **kwargs):
    data = GroupService(conn).get_groups()
    logger.info(f"Fetched members: {data}")
    return {"data": data}


@db_context_manager
def get_member_fees(conn, group_id, year, month, **kwargs):
    data = GroupService(conn).get_member_fees(group_id, year, month)
    logger.info(f"Fetched member fees: {data}")
    return {"data": data}
