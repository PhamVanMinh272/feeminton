from flask import request, Blueprint

from src.api_logic import reservations


attendances_router = Blueprint("attendances", __name__)

@attendances_router.route("/<int:attendance_id>", methods=["PATCH"])
def patch_attendance(attendance_id):
    data = request.json
    joined = data.get("joined")
    return reservations.patch_attendance(attendance_id=attendance_id, joined=joined)