from src.data_repo.member_repo import MemberRepo


class MemberService:
    def __init__(self, conn):
        self._conn = conn
        self.members = None

    def get_members(self):
        """
        Get all members.
        :return:
        """
        return MemberRepo(self._conn).get_all_members()

    def get_member(self, member_id: int):
        """
        Get a member by ID.
        :return:
        """
        return MemberRepo(self._conn).get_member_by_id(member_id)
