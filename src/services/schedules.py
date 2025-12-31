
import datetime
import calendar
from typing import List, Dict, Optional


from src.data_repo.schedule_repo import ScheduleRepo
from src.schemas.pydantic_models.schedules import NewScheduleModel
from src.settings import logger


class ScheduleService:
    def __init__(self, conn):
        self._conn = conn
        self.schedules = ScheduleRepo(self._conn).get_all_schedules()

    @staticmethod
    def _current_month_range() -> tuple[datetime.date, datetime.date]:
        """
        Returns (first_day, last_day) of the current month.
        """
        today = datetime.date.today()
        first_day = today.replace(day=1)
        # calendar.monthrange(year, month) -> (weekday_of_first_day, number_of_days_in_month)

        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        return first_day, last_day

    def get_schedules(
            self,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get reservations within a date range (defaults to the current month),
        and attach their associated attendances.

        :param start_date: 'YYYY-MM-DD' string (inclusive), optional
        :param end_date: 'YYYY-MM-DD' string (inclusive), optional
        :return: List of reservations with 'attendances' field
        """
        logger.info(f"Fetching schedules with start_date={start_date}, end_date={end_date}")
        # Determine date range
        if start_date and end_date:
            try:
                start_dt = datetime.date.fromisoformat(start_date)
                end_dt = datetime.date.fromisoformat(end_date)
            except ValueError as e:
                raise ValueError("start_date/end_date must be ISO format 'YYYY-MM-DD'") from e
        else:
            start_dt, end_dt = self._current_month_range()
            logger.info(f"No date range provided, defaulting to current month: {start_dt} to {end_dt}")

        if end_dt < start_dt:
            raise ValueError("end_date must be >= start_date")

        # Filter reservations within [start_dt, end_dt]
        filtered: List[Dict] = []
        print(self.schedules)

        for r in self.schedules or []:
            r_date_str = r.get("schedule_date")
            if not r_date_str:
                # Skip if reservation has no date
                continue
            try:
                r_date = datetime.date.fromisoformat(r_date_str[:10])  # handle potential 'YYYY-MM-DD...' strings
            except ValueError:
                # Skip malformed date strings
                continue
            print(r_date)
            print(start_dt, end_dt)
            if start_dt <= r_date <= end_dt:
                filtered.append(r)
        print(filtered)
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

    def create_schedule(self, schedule_data):
        """
        Create a new reservation.
        Auto create attendances for all members.
        :param schedule_data:
        :return:
        """
        new_reservation = NewScheduleModel(**schedule_data)
        schedule_id = ScheduleRepo(self._conn).create_schedule(new_reservation)
        ScheduleRepo(self._conn).create_attendances_for_all_members(schedule_id)
        return schedule_id

    def patch_attendance(self, attendance_id, joined):
        """
        Patch attendance status.
        :return:
        """
        refund_amount = 20 if not joined else 0
        ScheduleRepo(self._conn).update_attendance(attendance_id, joined, refund_amount)
