from Singleton import Singleton
from ChangeTicket import ChangeTicket
from ApiService import ApiService
from datetime import date

class ActivityGenerator(Singleton):
    _initialized = False
    _current_change_ticket = None

    def __init__(self):
        if not self._initialized:
            _initialized = True

    def generate_activities_for_change(self, change_ticket: ChangeTicket):
        self._current_change_ticket = change_ticket

        self.generate_manager_activity()
        self.generate_payroll_activity()

        if self._current_change_ticket.ORDER_ACCESS_KEYS is not None and self._current_change_ticket.ORDER_ACCESS_KEYS == "Yes":
            self.generate_reception_activity()

    def generate_manager_activity(self):
        ApiService().create_new_activity(
            self._current_change_ticket.id,
            "AT-040",
            str(date.today()),
            str(self._current_change_ticket.start_date),
            "testing features for now"
            # request_description
        )

    def generate_payroll_activity(self):
        ApiService().create_new_activity(
            self._current_change_ticket.id,
            "AT-041",
            str(date.today()),
            str(self._current_change_ticket.start_date),
            "testing features for now"
            # request_description
        )

    def generate_reception_activity(self):
        ApiService().create_new_activity(
            self._current_change_ticket.id,
            "AT-042",
            str(date.today()),
            str(self._current_change_ticket.start_date),
            "testing features for now"
            # request_description
        )