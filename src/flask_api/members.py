from flask import Blueprint

from src.api_logic import members

members_router = Blueprint("members", __name__)


@members_router.route("", methods=["GET"])
def get_members():
    return members.get_members()


@members_router.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
    return members.get_member(member_id)
