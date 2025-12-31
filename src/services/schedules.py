
import datetime
import calendar
from typing import List, Dict, Optional, Tuple

from src.data_repo.schedule_repo import ScheduleRepo
from src.schemas.pydantic_models.schedules import NewScheduleModel, SearchScheduleModel
from src.settings import logger


class ScheduleService:
    def __init__(self, conn):
        self._conn = conn
        self.schedules = None

    @staticmethod
    def _month_range(year: Optional[int] = None, month: Optional[int] = None) -> Tuple[
        datetime.date, datetime.date]:
        """
        Returns (first_day, last_day) for the specified year/month.
        If year or month is None, defaults to the current month.
        """
        today = datetime.date.today()
        y = year if year is not None else today.year
        m = month if month is not None else today.month

        # Basic validation
        if not (1 <= int(m) <= 12):
            raise ValueError("month must be an integer in the range 1..12")

        # Ensure y, m are ints (in case they come as strings from query params)
        y = int(y)
        m = int(m)

        first_day = datetime.date(y, m, 1)
        last_day = datetime.date(y, m, calendar.monthrange(y, m)[1])
        return first_day, last_day

    @staticmethod
    def _current_month_range() -> Tuple[datetime.date, datetime.date]:
        """
        Backward-compatible helper: returns (first_day, last_day) of the current month.
        """
        return ScheduleService._month_range()

    def get_schedules(
            self,
            params: SearchScheduleModel
    ) -> List[Dict]:
        """
        Get reservations within a date range (defaults to the current month),
        and attach their associated attendances.

        :return: List of reservations with 'attendances' field
        """

        # Compute range (fallback to current month)
        try:
            start_dt, end_dt = self._month_range(params.year, params.month)
        except Exception:
            # Defensive fallback if bad inputs are provided
            start_dt, end_dt = self._current_month_range()

        if end_dt < start_dt:
            raise ValueError("end_date must be >= start_date")

        # Filter reservations within [start_dt, end_dt]
        filtered: List[Dict] = []
        self.schedules = ScheduleRepo(self._conn).get_all_schedules(group_id=params.group_id)

        for r in self.schedules or []:
            r_date_str = r.get("scheduleDate")
            if not r_date_str:
                # Skip if reservation has no date
                continue
            try:
                r_date = datetime.date.fromisoformat(r_date_str[:10])  # handle potential 'YYYY-MM-DD...' strings
            except ValueError:
                # Skip malformed date strings
                continue
            if start_dt <= r_date <= end_dt:
                filtered.append(r)
        response_data: List[Dict] = []
        repo = ScheduleRepo(self._conn)

        for schedule in filtered:
            # If your get_attendances_by_reservation_id supports date range, pass it.
            # Otherwise, remove start/end params.
            attendances = repo.get_attendances_by_schedule_id(
                schedule_id=schedule["id"],
                start_date=start_dt.isoformat(),
                end_date=end_dt.isoformat(),
            )
            reservation_with_attendances = dict(schedule)
            reservation_with_attendances["attendances"] = attendances
            response_data.append(reservation_with_attendances)

        return response_data

    def get_schedule(self, schedule_id: int):
        """
        Get a schedule by ID. And its attendances.
        :return:
        """
        schedule = ScheduleRepo(self._conn).get_schedule_by_id(schedule_id)
        if not schedule:
            return None
        attendances = ScheduleRepo(self._conn).get_attendances_by_schedule_id(schedule_id)
        schedule["attendances"] = attendances
        return schedule

    def _get_schedule_by_attendance_id(self, attendance_id: int):
        """
        Get schedule by attendance ID.
        :return:
        """
        return ScheduleRepo(self._conn).get_schedule_by_attendance_id(attendance_id)

    def create_schedule(self, schedule_data):
        """
        Create a new reservation.
        Auto create attendances for all members.
        :param schedule_data:
        :return:
        """
        new_reservation = NewScheduleModel(**schedule_data)
        schedule_id = ScheduleRepo(self._conn).create_schedule(new_reservation)
        ScheduleRepo(self._conn).create_attendances_for_group_members(schedule_id)
        return schedule_id

    def patch_attendance(self, attendance_id, joined) -> dict:
        """
        Patch attendance status.
        :return:
        """

        refund_amount = 0
        ScheduleRepo(self._conn).update_attendance(attendance_id, joined, refund_amount)

        logger.info(f"Calculating refund for attendance ID {attendance_id} with joined={joined}")
        schedule = self._get_schedule_by_attendance_id(attendance_id)
        self._update_refunds_for_dropouts(schedule["id"])

        data = ScheduleRepo(self._conn).get_attendance_by_id(attendance_id)
        if not data:
            raise ValueError(f"Attendance with ID {attendance_id} does not exist.")
        logger.info(f"Updated attendance: {data}")
        return data

    def _update_refunds_for_dropouts(self, schedule_id: int):
        """
        Recalculate and update refund amounts for all dropouts in a schedule.
        :param schedule_id:
        :return:
        """
        # hard code
        min_fee_groups = {
            1: 40,
            2: 90,
        }
        max_refund_groups = {
            1: 40,
            2: 50,
        }
        """
        New logic:
        Refund amount logic:
        refund_amount = int(min_fee_groups.get(group_id, 50) / drop_out_count)
        """
        # end hard code
        # update refund amounts for other dropouts

        schedule = ScheduleRepo(self._conn).get_schedule_by_id(schedule_id)
        all_attendances = ScheduleRepo(self._conn).get_attendances_by_schedule_id(schedule_id)
        drop_out_count = sum(1 for att in all_attendances if not att["joined"])
        refund_amount = int(min_fee_groups.get(schedule["groupId"], 50) / drop_out_count) if drop_out_count > 0 else 0
        # check max refund
        max_refund = max_refund_groups.get(schedule["groupId"], 50)
        if refund_amount > max_refund:
            refund_amount = max_refund
        for att in all_attendances:
            if not att["joined"]:
                ScheduleRepo(self._conn).update_attendance(att["attendanceId"], False, refund_amount)
        logger.info(f"Updated refund amounts for dropouts in schedule ID {schedule_id} to {refund_amount}")
