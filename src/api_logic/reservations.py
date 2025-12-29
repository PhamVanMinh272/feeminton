from src.settings import logger
from src.services.reservations import ReservationService
from src.common.db_connection import db_context_manager

@db_context_manager
def get_reservations(conn, **kwargs):
    reservations = ReservationService(conn).get_reservations()
    logger.info(f"Fetched reservations: {reservations}")
    return {"data": reservations}

@db_context_manager
def create_reservation(conn, reservation_data, **kwargs):
    reservation_id = ReservationService(conn).create_reservation(reservation_data)
    logger.info(f"Created reservation with ID: {reservation_id}")
    return {"reservation_id": reservation_id}

@db_context_manager
def patch_attendance(conn, attendance_id, joined, **kwargs):
    ReservationService(conn).patch_attendance(attendance_id, joined)
    logger.info(f"Patched attendance ID: {attendance_id} with joined: {joined}")
    return {"status": "success"}
