from ChangeTicket import ChangeTicket
from ApiService import ApiService
from datetime import date
from OnboardingSettings import OnboardingSettings

class ActivityGenerator():
    def generate_activities_for_change(self, change_ticket: ChangeTicket):
        templates = OnboardingSettings().get_activities_for_change_template(change_ticket.template_number)

        for template in templates:
            settings = ApiService().get_asset(id=template) #  DK entry

            request_description = ""
            fields = settings.get("data").get("fields-1").split("\n")
            for field in fields:
                request_description += f"{field}: {change_ticket.as_dictionary.get(field)}\n"

            receiver = settings.get("data").get("receiver-s-email")
            if receiver == "MANAGER":
                receiver_id = ApiService().lookup_manager(name=change_ticket.manager).get('results')[0].get('id')
                receiver = ApiService().get_person_by_id(receiver_id).get("email")

            activity = ApiService().create_new_activity(
                change_name=change_ticket.id,
                activity_template_name=settings.get("data").get("activity-template"),
                start_date=str(date.today()),
                end_date=str(change_ticket.start_date),
                request_description=request_description,
                assignee=receiver
            )

            ApiService().solve_activity(activity.get("id"))