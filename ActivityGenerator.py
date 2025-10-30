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
        request_description = "testing features for now"
        assignee = "Claudiu.Jechel@dlf.com"

        ApiService().create_new_activity(
            change_name=self._current_change_ticket.id,
            activity_template_name="AT-040",
            start_date=str(date.today()),
            end_date=str(self._current_change_ticket.start_date),
            request_description=request_description,
            assignee=assignee
        )

    def generate_payroll_activity(self):
        request_description = f"Name: {self._current_change_ticket.fullname} \nCPR: {self._current_change_ticket.cpr}\nStart date: {self._current_change_ticket.start_date}"
        assignee = "Claudiu.Jechel@dlf.com"

        ApiService().create_new_activity(
            change_name=self._current_change_ticket.id,
            activity_template_name="AT-041",
            start_date=str(date.today()),
            end_date=str(self._current_change_ticket.start_date),
            request_description=request_description,
            assignee=assignee
        )

    def generate_reception_activity(self):
        request_description = f"Name: {self._current_change_ticket.fullname}\nStart date: {self._current_change_ticket.start_date}"
        assignee = "Claudiu.Jechel@dlf.com"

        ApiService().create_new_activity(
            change_name=self._current_change_ticket.id,
            activity_template_name="AT-042",
            start_date=str(date.today()),
            end_date=str(self._current_change_ticket.start_date),
            request_description=request_description,
            assignee=assignee
        )