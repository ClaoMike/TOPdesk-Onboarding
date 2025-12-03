from ChangeTicket import ChangeTicket
from ApiService import ApiService
from datetime import date

class ActivityGenerator():
    def generate_activities_for_change(self, change_ticket: ChangeTicket):
        asset = ApiService().get_asset(id="625d58ac-8042-4478-93cf-a72b02336896") # asset that contains the settings

        for entry in  asset.get("data").get("@gridwidgetfield_00a6f1d9-1a29-4c45-9994-70ee3dc3b5aa"):
            settings = ApiService().get_asset(id=entry) #  DK entry

            request_description = ""
            fields = settings.get("data").get("fields-1").split("\n")
            for field in fields:
                request_description += f"{field}: {change_ticket.as_dictionary.get(field)}\n"

            ApiService().create_new_activity(
                change_name=change_ticket.id,
                activity_template_name=settings.get("data").get("activity-template"),
                start_date=str(date.today()),
                end_date=str(change_ticket.start_date),
                request_description=request_description,
                assignee=settings.get("data").get("receiver-s-email")
            )