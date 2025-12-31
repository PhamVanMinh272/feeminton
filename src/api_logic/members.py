from src.settings import logger
from src.services.members import MemberService
from src.common.db_connection import db_context_manager

@db_context_manager
def get_members(conn, **kwargs):
    members = MemberService(conn).get_members()
    logger.info(f"Fetched members: {members}")
    return {"data": members}

@db_context_manager
def get_member(conn, member_id, **kwargs):
    member = MemberService(conn).get_member(member_id)
    logger.info(f"Fetched member: {member}")
    return {"data": member}