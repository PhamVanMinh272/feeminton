from typing import Optional, List, Dict
from src.schemas.pydantic_models.schedules import NewScheduleModel


class ScheduleRepo:

    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def get_all_schedules(self, group_id: int) -> list[dict]:
        self._cursor.execute(
            """
            SELECT schedules.id, schedule_date
            FROM schedules where group_id = ?
            ORDER BY schedule_date DESC""",
            (group_id,),
        )
        rows = self._cursor.fetchall()
        sections = [
            {
                "id": row[0],
                "scheduleDate": row[1]
            }
            for row in rows
        ]
        return sections

    def get_schedule_by_id(self, schedule_id: int) -> Optional[dict]:
        self._cursor.execute(
            """
            SELECT schedules.id, schedule_date, group_id
            FROM schedules WHERE schedules.id = ?
            """,
            (schedule_id,),
        )
        row = self._cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "scheduleDate": row[1],
                "groupId": row[2],
            }
        return None

    def create_schedule(self, schedule_data: NewScheduleModel) -> int:
        self._cursor.execute(
            """
            INSERT INTO schedules (schedule_date, group_id) VALUES (?, ?)
            """,
            (
                schedule_data.schedule_date.strftime("%Y-%m-%dT%H:%M:%S"),
                schedule_data.group_id,
            ),
        )
        reservation_id = self._cursor.lastrowid
        # commit
        self._cursor.connection.commit()
        return reservation_id

    def create_attendances_for_group_members(self, schedule_id: int) -> int:
        """
        Insert attendance rows for all members that belong to the schedule's group.
        Uses INSERT OR IGNORE (SQLite) to avoid duplicate rows (requires unique index).
        Returns the number of rows that would be inserted (i.e., those not yet present).
        """
        # Count how many members still need attendance for this schedule
        precheck_sql = """
            SELECT COUNT(*)
            FROM schedules s
            JOIN members  m ON m.group_id = s.group_id
            LEFT JOIN attendance a
                   ON a.schedule_id = s.id AND a.member_id = m.id
            WHERE s.id = ?
              AND a.id IS NULL
        """
        self._cursor.execute(precheck_sql, (schedule_id,))
        to_insert = int(self._cursor.fetchone()[0])

        insert_sql = """
            INSERT OR IGNORE INTO attendance (member_id, schedule_id, joined, refund_amount)
            SELECT m.id, s.id, 1, 0
            FROM schedules s
            JOIN members  m ON m.group_id = s.group_id
            WHERE s.id = ?
        """
        self._cursor.execute(insert_sql, (schedule_id,))
        self._cursor.connection.commit()

        # Optionally return the number of new rows
        return to_insert

    def get_attendances_by_schedule_id(
            self,
            schedule_id: int,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
    ) -> List[Dict]:
        where = ["a.schedule_id = ?"]
        params = [schedule_id]

        if start_date and end_date:
            if end_date < start_date:
                raise ValueError("end_date must be >= start_date.")
            where.append("DATE(r.schedule_date) BETWEEN DATE(?) AND DATE(?)")
            params.extend([start_date, end_date])
        elif start_date:
            where.append("DATE(r.schedule_date) >= DATE(?)")
            params.append(start_date)
        elif end_date:
            where.append("DATE(r.schedule_date) <= DATE(?)")
            params.append(end_date)

        sql = f"""
            SELECT
                a.id, m.id, m.nickname, a.joined, a.refund_amount
            FROM attendance AS a
            JOIN members      AS m ON a.member_id = m.id
            JOIN schedules AS r ON r.id = a.schedule_id
            WHERE {' AND '.join(where)}
            ORDER BY m.nickname COLLATE NOCASE, a.id
        """
        self._cursor.execute(sql, params)
        rows = self._cursor.fetchall()

        return [
            {
                "attendanceId": row[0],
                "memberId": row[1],
                "memberName": row[2],
                "joined": bool(row[3]),
                "refundAmount": row[4],
            }
            for row in rows
        ]

    def get_schedule_by_attendance_id(self, attendance_id: int) -> Optional[dict]:
        self._cursor.execute(
            """
            SELECT
                s.id, s.schedule_date, s.group_id
            FROM schedules AS s
            JOIN attendance AS a ON a.schedule_id = s.id
            WHERE a.id = ?
            """,
            (attendance_id,),
        )
        row = self._cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "scheduleDate": row[1],
                "groupId": row[2],
            }
        return None

    def update_attendance(self, attendance_id: int, joined: bool, refund_amount: int):
        self._cursor.execute(
            """
            UPDATE attendance
            SET joined = ?, refund_amount = ?
            WHERE id = ?
            """,
            (int(joined), refund_amount, attendance_id),
        )
        # commit
        self._cursor.connection.commit()
        return

    def get_attendance_by_id(self, attendance_id: int) -> Optional[dict]:
        self._cursor.execute(
            """
            SELECT
                a.id, m.id, m.nickname, a.joined, a.refund_amount
            FROM attendance AS a
            JOIN members      AS m ON a.member_id = m.id
            WHERE a.id = ?
            """,
            (attendance_id,),
        )
        row = self._cursor.fetchone()
        if row:
            return {
                "attendanceId": row[0],
                "memberId": row[1],
                "memberName": row[2],
                "joined": bool(row[3]),
                "refundAmount": row[4],
            }
        return None
