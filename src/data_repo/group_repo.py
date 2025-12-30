class GroupRepo:
    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def get_all_groups(self):
        self._cursor.execute("SELECT id, name FROM groups")
        rows = self._cursor.fetchall()
        data = [{"id": row[0], "name": row[1]} for row in rows]
        return data
