from flask import request, Blueprint

from src.api_logic import schedules


schedules_router = Blueprint("reservations", __name__)


@schedules_router.route("", methods=["GET"])
def get_all_reservations():
    return schedules.get_schedules(**request.args)

@schedules_router.route("/<int:schedule_id>", methods=["GET"])
def get_reservation(schedule_id):
    return schedules.get_schedule(schedule_id=schedule_id)

@schedules_router.route("", methods=["POST"])
def create_reservation():
    return schedules.create_schedule(schedule_data=request.json)

@schedules_router.route("/attendance/<int:attendance_id>", methods=["PATCH"])
def patch_attendance(attendance_id):
    data = request.json
    joined = data.get("joined")
    return schedules.patch_attendance(attendance_id=attendance_id, joined=joined)


@schedules_router.route("/<int:schedule_id>", methods=["DELETE"])
def delete_reservation(schedule_id):
    return schedules.delete_schedule(schedule_id=schedule_id)