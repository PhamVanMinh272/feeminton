class MemberRepo:
    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def get_all_members(self):
        self._cursor.execute("SELECT id, name, gender FROM members")
        rows = self._cursor.fetchall()
        players = [{"id": row[0], "name": row[1], "gender": row[2]} for row in rows]
        return players
