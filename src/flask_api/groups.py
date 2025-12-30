from flask import Blueprint

from src.api_logic import groups

groups_router = Blueprint("groups", __name__)


@groups_router.route("", methods=["GET"])
def get_groups():
    return groups.get_groups()
