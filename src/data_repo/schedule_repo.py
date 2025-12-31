from typing import Optional, List, Dict
from src.schemas.pydantic_models.schedules import NewScheduleModel


class ScheduleRepo:

    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def get_all_schedules(self) -> list[dict]:
        self._cursor.execute(
            """
            SELECT schedules.id, schedule_date
            FROM schedules 
            ORDER BY schedule_date DESC"""
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

    def create_attendances_for_all_members(self, schedule_id: int):
        self._cursor.execute(
            """
            INSERT INTO attendance (member_id, schedule_id, joined, refund_amount)
            SELECT id, ?, 1, 0 FROM members
            """,
            (schedule_id,),
        )
        # commit
        self._cursor.connection.commit()
        return

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

    # def get_all_templates(self) -> list[dict]:
    #     self._cursor.execute(
    #         """
    #     SELECT
    #     template.id,
    #     template.name,
    #     billing_type_id,
    #     rental_cost,
    #     shuttle_amount,
    #     shuttle_price,
    #     day_index,
    #     GROUP_CONCAT(player.name, ',') as player_name FROM template
    #     join template_player on template.id = template_player.template_id
    #     join player on template_player.player_id = player.id
    #     GROUP BY template.id,
    #     template.name,
    #     billing_type_id,
    #     rental_cost,
    #     shuttle_amount,
    #     shuttle_price
    #     """
    #     )
    #     rows = self._cursor.fetchall()
    #     players = [
    #         {
    #             "id": row[0],
    #             "name": row[1],
    #             "billingType": row[2],
    #             "rentalCost": row[3],
    #             "shuttleAmount": row[4],
    #             "shuttlePrice": row[5],
    #             "day": row[6],
    #             "players": [i for i in row[7].split(",") if i],
    #         }
    #         for row in rows
    #     ]
    #     return players
    #
    # def add_session(self, session_data: dict) -> int:
    #     self._cursor.execute(
    #         """
    #         INSERT INTO practice_session (name, session_date, shift_time, location) VALUES (?, ?, ?, ?)
    #         """,
    #         (
    #             session_data["name"],
    #             session_data["sessionDate"],
    #             session_data["shiftTime"],
    #             session_data["location"],
    #         ),
    #     )
    #     session_id = self._cursor.lastrowid
    #     # commit
    #     self._cursor.connection.commit()
    #     return session_id
    #
    # def get_billing_types(self) -> list[dict]:
    #     self._cursor.execute("SELECT id, name FROM billing_type")
    #     rows = self._cursor.fetchall()
    #     billing_types = [{"id": row[0], "name": row[1]} for row in rows]
    #     return billing_types
