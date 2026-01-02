from flask import Blueprint

from src.api_logic import groups

groups_router = Blueprint("groups", __name__)


@groups_router.route("", methods=["GET"])
def get_groups():
    return groups.get_groups()


@groups_router.route("/<int:group_id>/fees/<int:year>/<int:month>", methods=["GET"])
def get_member_fees(group_id, year, month):
    return groups.get_member_fees(group_id, year, month)
