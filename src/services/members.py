from src.data_repo.member_repo import MemberRepo


class MemberService:
    def __init__(self, conn):
        self._conn = conn
        self.members = MemberRepo(self._conn).get_all_members()

    def get_members(self):
        """
        Get all members.
        :return:
        """
        return self.members
