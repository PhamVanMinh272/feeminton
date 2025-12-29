from flask import Blueprint

from src.api_logic import members

members_router = Blueprint("member", __name__)


@members_router.route("", methods=["GET"])
def get_members():
    return members.get_members()
