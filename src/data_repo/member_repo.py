from src.settings import logger


class MemberRepo:
    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def get_all_members(self):
        self._cursor.execute("SELECT id, nickname, group_id FROM members")
        rows = self._cursor.fetchall()
        players = [
            {"id": row[0], "name": row[1], "group": {"id": row[2]}} for row in rows
        ]
        return players

    def get_member_by_id(self, member_id: int):
        """
        Get a member by ID.
        - basic info
        - refund amount for all schedules of current month
        - estimated bill for next month
        """
        logger.info(f"Fetching member with ID {member_id}")
        self._cursor.execute(
            "SELECT members.id, nickname, group_id, gender, member_fee FROM members join users on members.user_id= users.id where members.id = ?",
            (member_id,),
        )
        row = self._cursor.fetchone()
        member = {
            "id": row[0],
            "nickname": row[1],
            "groupId": row[2],
            "gender": row[3],
            "memberFee": row[4],
        }

        # refund amount for all schedules of current month
        self._cursor.execute(
            """
            SELECT SUM(refund_amount) 
            FROM attendance a 
            JOIN schedules s ON a.schedule_id = s.id 
            WHERE a.member_id = ? 
            AND a.joined = 0 
            AND strftime('%Y-%m', s.schedule_date) = strftime('%Y-%m', 'now')
        """,
            (member_id,),
        )
        refund_row = self._cursor.fetchone()
        member["currentMonthRefund"] = refund_row[0] if refund_row[0] is not None else 0

        # next month fee = unit_fee*schedules_amount - refund this month
        # count of schedules for next month
        self._cursor.execute(
            """
            SELECT COUNT(*) 
            FROM schedules 
            WHERE group_id = ? 
            AND strftime('%Y-%m', schedule_date) = strftime('%Y-%m', 'now', '+1 month')
        """,
            (member["groupId"],),
        )
        schedule_count_row = self._cursor.fetchone()
        schedule_count = (
            schedule_count_row[0] if schedule_count_row[0] is not None else 0
        )
        logger.info(
            f"Member ID {member_id} - Schedule count for next month: {schedule_count}"
        )

        estimated_bill = (
            member["memberFee"] * schedule_count - member["currentMonthRefund"]
        )

        member["estimatedBillNextMonth"] = estimated_bill if estimated_bill > 0 else 0
        return member
