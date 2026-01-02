class GroupRepo:
    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def get_all_groups(self):
        sql = """
            SELECT
                g.id   AS group_id,
                g.name AS group_name,
                m.id   AS member_id,
                m.nickname AS member_nickname
            FROM groups AS g
            LEFT JOIN members AS m
                ON m.group_id = g.id
            ORDER BY g.id, m.id
        """
        self._cursor.execute(sql)
        rows = self._cursor.fetchall()

        groups_by_id = {}
        for group_id, group_name, member_id, member_nickname in rows:
            if group_id not in groups_by_id:
                groups_by_id[group_id] = {
                    "id": group_id,
                    "name": group_name,
                    "members": [],
                }
            # Only append a member if it exists (LEFT JOIN yields NULLs for groups without members)
            if member_id is not None:
                groups_by_id[group_id]["members"].append(
                    {"id": member_id, "nickname": member_nickname}
                )

        return list(groups_by_id.values())

    # def get_month_member_fees(self, group_id: int, year: int, month: int):
    #     """
    #     fee member monthly = member_fee*scgedules_amount - sum(refund_amount previously)
    #     :param group_id:
    #     :param year:
    #     :param month:
    #     :return:
    #     """
    #     sql = """
    #         SELECT
    #             m.id AS member_id,
    #             m.nickname AS member_nickname,
    #             m.member_fee AS member_fee,
    #             COUNT(s.id) AS schedule_count,
    #             IFNULL(SUM(a.refund_amount), 0) AS total_refund
    #         FROM members AS m
    #         LEFT JOIN schedules AS s
    #             ON s.group_id = m.group_id
    #             AND strftime('%Y', s.schedule_date) = ?
    #             AND strftime('%m', s.schedule_date) = ?
    #         LEFT JOIN attendance AS a
    #             ON a.schedule_id = s.id
    #             AND a.member_id = m.id
    #         WHERE m.group_id = ?
    #         GROUP BY m.id, m.nickname, m.member_fee
    #         ORDER BY m.nickname COLLATE NOCASE
    #     """
    #     params = (str(year), f"{month:02d}", group_id)
    #     self._cursor.execute(sql, params)
    #     rows = self._cursor.fetchall()
    #
    #     member_fees = []
    #     for (
    #         member_id,
    #         member_nickname,
    #         member_fee,
    #         schedule_count,
    #         total_refund,
    #     ) in rows:
    #         estimated_fee = (member_fee * schedule_count) - total_refund
    #         member_fees.append(
    #             {
    #                 "memberId": member_id,
    #                 "memberNickname": member_nickname,
    #                 "estimatedFee": estimated_fee,
    #             }
    #         )
    #
    #     return member_fees

    def get_month_member_fees(self, group_id: int, year: int, month: int):
        """
        Calculate monthly fees for members:
        estimated_fee = (member_fee * schedule_count in given month) - total_refund(previous month)
        """
        # Determine previous month/year
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        sql = """
            SELECT
                m.id AS member_id,
                m.nickname AS member_nickname,
                m.member_fee AS member_fee,
                COUNT(DISTINCT s.id) AS schedule_count,
                IFNULL(SUM(r.refund_amount), 0) AS total_refund
            FROM members AS m
            -- schedules in current month
            LEFT JOIN schedules AS s
                ON s.group_id = m.group_id
                AND strftime('%Y', s.schedule_date) = ?
                AND strftime('%m', s.schedule_date) = ?
            -- refunds from previous month
            LEFT JOIN schedules AS ps
                ON ps.group_id = m.group_id
                AND strftime('%Y', ps.schedule_date) = ?
                AND strftime('%m', ps.schedule_date) = ?
            LEFT JOIN attendance AS r
                ON r.schedule_id = ps.id
                AND r.member_id = m.id
            WHERE m.group_id = ?
            GROUP BY m.id
            ORDER BY m.nickname COLLATE NOCASE
        """
        params = (
            str(year), f"{month:02d}",  # schedules for current month
            str(prev_year), f"{prev_month:02d}",  # refunds for previous month
            group_id,
        )
        self._cursor.execute(sql, params)
        rows = self._cursor.fetchall()

        member_fees = []
        for member_id, member_nickname, member_fee, schedule_count, total_refund in rows:
            estimated_fee = (member_fee * schedule_count) - total_refund
            member_fees.append({
                "memberId": member_id,
                "memberNickname": member_nickname,
                "memberFee": member_fee,
                "scheduleCount": schedule_count,
                "totalRefund": total_refund,
                "estimatedFee": estimated_fee,
            })

        return member_fees
