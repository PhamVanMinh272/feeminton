from src.schemas.pydantic_models.schedules import SearchScheduleModel
from src.settings import logger
from src.services.schedules import ScheduleService
from src.common.db_connection import db_context_manager


@db_context_manager
def get_schedules(conn, **kwargs):
    params = SearchScheduleModel(**kwargs)
    data = ScheduleService(conn).get_schedules(params)
    logger.info(f"Fetched schedules: {data}")
    return {"data": data}


@db_context_manager
def get_schedule(conn, schedule_id, **kwargs):
    data = ScheduleService(conn).get_schedule(schedule_id)
    logger.info(f"Fetched schedule: {data}")
    return {"data": data}


@db_context_manager
def create_schedule(conn, schedule_data, **kwargs):
    reservation_id = ScheduleService(conn).create_schedule(schedule_data)
    logger.info(f"Created schedule with ID: {reservation_id}")
    return {"scheduleId": reservation_id}


@db_context_manager
def patch_attendance(conn, attendance_id, joined, **kwargs):
    data = ScheduleService(conn).patch_attendance(attendance_id, joined)
    logger.info(f"Patched attendance ID: {attendance_id} with joined: {joined}")
    return {"data": data}


@db_context_manager
def delete_schedule(conn, schedule_id, **kwargs):
    ScheduleService(conn).delete_schedule(schedule_id)
    logger.info(f"Deleted schedule with ID: {schedule_id}")
    return {"status": "success"}
