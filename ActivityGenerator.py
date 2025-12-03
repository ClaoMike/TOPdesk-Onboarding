from Singleton import Singleton
from ChangeTicket import ChangeTicket
from ApiService import ApiService
from datetime import date

class ActivityGenerator(Singleton):
    _current_change_ticket = None

    def _init_singleton(self):
        pass

    def generate_activities_for_change(self, change_ticket: ChangeTicket):
        self._current_change_ticket = change_ticket

        self.generate_manager_activity()
        self.generate_payroll_activity()
        self.generate_heidi_christiansen()

        if self._current_change_ticket.ORDER_ACCESS_KEYS is not None and self._current_change_ticket.ORDER_ACCESS_KEYS == "Yes":
            self.generate_reception_activity()

    def generate_manager_activity(self):
        request_description = f"""
            Name: {self._current_change_ticket.fullname}\n
            Email: {self._current_change_ticket.email}\n
            Personal phone number: {self._current_change_ticket.personal_phone_number}\n
            Address: {self._current_change_ticket.address}\n
            Date of birth: {self._current_change_ticket.date_of_birth}\n
            Department: {self._current_change_ticket.department}\n
            Employee type: {self._current_change_ticket.employee_type}\n
            Job title: {self._current_change_ticket.job_title}\n
            Start date: {self._current_change_ticket.start_date}\n
            End date: {self._current_change_ticket.end_date}\n
            Hire reason: {self._current_change_ticket.hire_reason}\n
        """

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

    def generate_heidi_christiansen(self):
        request_description = f"Name: {self._current_change_ticket.fullname}\nEnd date: {self._current_change_ticket.end_date}"
        assignee = "Claudiu.Jechel@dlf.com"

        ApiService().create_new_activity(
            change_name=self._current_change_ticket.id,
            activity_template_name="AT-042",
            start_date=str(date.today()),
            end_date=str(self._current_change_ticket.start_date),
            request_description=request_description,
            assignee=assignee
        )

