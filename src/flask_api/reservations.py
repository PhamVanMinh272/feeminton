from flask import request, Blueprint

from src.api_logic import reservations


reservations_router = Blueprint("reservations", __name__)


@reservations_router.route("", methods=["GET"])
def get_all_reservations():
    return reservations.get_reservations()

@reservations_router.route("", methods=["POST"])
def create_reservation():
    return reservations.create_reservation(reservation_data=request.json)

@reservations_router.route("/attendance/<int:attendance_id>", methods=["PATCH"])
def patch_attendance(attendance_id):
    data = request.json
    joined = data.get("joined")
    return reservations.patch_attendance(attendance_id=attendance_id, joined=joined)




# @session_router.route("", methods=["POST"])
# def add_session():
#     return reservations.add_session(**request.json)
#
#
# @session_router.route("/templates", methods=["GET"])
# def get_session_templates():
#     return reservations.get_session_templates()
#
#
# @session_router.route("/attributes-data", methods=["GET"])
# def get_session_attributes_data():
#     return reservations.get_session_attributes_data()
#
#
# @session_router.route("/calc-cost-weighted", methods=["POST"])
# def calc_cost_weighted():
#     data = request.json
#     return reservations.calc_cost_api_logic(**data)
#
#
# @session_router.route("/calc-cost-equally", methods=["POST"])
# def calc_cost_equally():
#     data = request.json
#     return reservations.calc_cost_equally(**data)
#
#
# @session_router.route("/billing-types", methods=["GET"])
# def get_billing_types():
#     return reservations.get_billing_types()
