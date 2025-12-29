from src.data_repo.reservation_repo import ReservationRepo
from src.schemas.pydantic_models.reservations import NewReservationModel


class ReservationService:
    def __init__(self, conn):
        self._conn = conn
        self.reservations = ReservationRepo(self._conn).get_all_reservations()

    def get_reservations(self):
        """
        Get all reservations.
        and their associated attendances.
        :return:
        """
        response_data = []
        for reservation in self.reservations:
            attendances = ReservationRepo(self._conn).get_attendances_by_reservation_id(reservation["id"])
            reservation_with_attendances = reservation.copy()
            reservation_with_attendances["attendances"] = attendances
            response_data.append(reservation_with_attendances)

        return response_data

    def create_reservation(self, reservation_data):
        """
        Create a new reservation.
        Auto create attendances for all members.
        :param reservation_data:
        :return:
        """
        new_reservation = NewReservationModel(**reservation_data)
        reservation_id = ReservationRepo(self._conn).create_reservation(new_reservation)
        ReservationRepo(self._conn).create_attendances_for_all_members(reservation_id)
        return reservation_id

    def patch_attendance(self, attendance_id, joined):
        """
        Patch attendance status.
        :return:
        """
        refund_amount = 20 if not joined else 0
        ReservationRepo(self._conn).update_attendance(attendance_id, joined, refund_amount)
