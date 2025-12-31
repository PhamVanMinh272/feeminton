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
                    "members": []
                }
            # Only append a member if it exists (LEFT JOIN yields NULLs for groups without members)
            if member_id is not None:
                groups_by_id[group_id]["members"].append({
                    "id": member_id,
                    "nickname": member_nickname
                })

        return list(groups_by_id.values())

