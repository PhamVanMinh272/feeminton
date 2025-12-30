from src.data_repo.group_repo import GroupRepo


class GroupService:
    def __init__(self, conn):
        self._conn = conn
        self.groups = None

    def get_groups(self):
        """
        Get all members.
        :return:
        """
        return GroupRepo(self._conn).get_all_groups()
