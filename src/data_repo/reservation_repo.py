from src.schemas.pydantic_models.reservations import NewReservationModel
class ReservationRepo:

    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def get_all_reservations(self) -> list[dict]:
        self._cursor.execute(
            """
            SELECT reservations.id, date
            FROM reservations 
            ORDER BY date DESC"""
        )
        rows = self._cursor.fetchall()
        sections = [
            {
                "id": row[0],
                "date": row[1]
            }
            for row in rows
        ]
        return sections

    def create_reservation(self, reservation_data: NewReservationModel) -> int:
        self._cursor.execute(
            """
            INSERT INTO reservations (date) VALUES (?)
            """,
            (
                reservation_data.date.strftime("%Y-%m-%dT%H:%M:%S"),
            ),
        )
        reservation_id = self._cursor.lastrowid
        # commit
        self._cursor.connection.commit()
        return reservation_id

    def create_attendances_for_all_members(self, reservation_id: int):
        self._cursor.execute(
            """
            INSERT INTO attendance (member_id, reservation_id, joined, refund_amount)
            SELECT id, ?, 1, 0 FROM members
            """,
            (reservation_id,),
        )
        # commit
        self._cursor.connection.commit()
        return

    def get_attendances_by_reservation_id(self, reservation_id: int) -> list[dict]:
        self._cursor.execute(
            """
            SELECT attendance.id, members.id, members.name, attendance.joined, attendance.refund_amount
            FROM attendance
            JOIN members ON attendance.member_id = members.id
            WHERE attendance.reservation_id = ?
            """,
            (reservation_id,),
        )
        rows = self._cursor.fetchall()
        attendances = [
            {
                "attendanceId": row[0],
                "memberId": row[1],
                "memberName": row[2],
                "joined": bool(row[3]),
                "refundAmount": row[4],
            }
            for row in rows
        ]
        return attendances

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
