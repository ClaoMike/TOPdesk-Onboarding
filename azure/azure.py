########################################################################################################################

import automationassets
import phonenumbers
import re
import requests
import sys
from abc import ABC, abstractmethod
from datetime import date, datetime
from email_validator import EmailNotValidError, validate_email
from phonenumbers import NumberParseException
from requests.auth import HTTPBasicAuth
from typing import Tuple, Union

########################################################################################################################

class Singleton(ABC):
    _instances = {}  # one instance per subclass

    def __new__(cls, *args, **kwargs):
        if cls is Singleton:
            raise TypeError("Singleton is abstract; subclass it instead.")

        # One instance per subclass
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            instance._initialized = False
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        # Only run initialization once per instance
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._init_singleton(*args, **kwargs)

    @abstractmethod
    def _init_singleton(self, *args, **kwargs):
        """Subclasses implement their one-time initialization here."""
        pass

########################################################################################################################

class AzureWebhookParser(Singleton):
    def _init_singleton(self):
        pass

    def parse_webhook(self):
        raw = ' '.join(sys.argv[4:])
        match = re.search(r'"?C\s\d{4}-\d{4}"?', raw)
        if match:
            return match.group(0).strip('"')
        else:
            raise Exception("The change id cannot be read from the passed webhook body.")

########################################################################################################################

class Configuration(Singleton):
    def _init_singleton(self):
        cred = automationassets.get_automation_credential("CREDENTIAL_TOPDESK_API")
        self.USERNAME = cred.get("username")
        self.PASSWORD = cred.get("password")

########################################################################################################################

class ApiService(Singleton):
    _topdesk_url = "https://dlfseeds.topdesk.net"

    def _init_singleton(self):
            self._authentication = HTTPBasicAuth(Configuration().USERNAME, Configuration().PASSWORD)

    def get_change(self, id: str):
        url = f"{self._topdesk_url}/tas/api/operatorChanges/{id}"
        headers = { "Content-Type": "application/json" }

        response = requests.get(url, headers=headers, auth=self._authentication)

        # --- Handle response ---
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

    def get_change_request(self, endpoint: str):
        url = f"{self._topdesk_url}{endpoint}"
        headers = { "Content-Type": "application/json" }

        response = requests.get(url, headers=headers, auth=self._authentication)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

    def lookup_manager(self, name: str):
        url = f"{self._topdesk_url}/tas/api/persons/lookup?name={name}"
        headers = { "Content-Type": "application/json" }

        response = requests.get(url, headers=headers, auth=self._authentication)

        # --- Handle response ---
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

    def reject_change(self, id: str, message: str):
        url = f"{self._topdesk_url}/tas/api/operatorChanges/{id}"
        headers = { "Content-Type": "application/json-patch+json" }
        json = [
            {
                "op": "add",
                "path": "/progressTrail",
                "value": message
            },
            {
                "op": "replace",
                "path": "/status",
                "value": "rejected"
            }
        ]

        response = requests.patch(url, headers=headers, auth=self._authentication, json=json)

        # --- Handle response ---
        if response.status_code > 200 and response.status_code < 300:
            pass
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

    def approve_change(self, id: str):
        url = f"{self._topdesk_url}/tas/api/operatorChanges/{id}"
        headers = { "Content-Type": "application/json-patch+json" }
        json = [
            {
                "op": "replace",
                "path": "/status",
                "value": "approved"
            }
        ]

        response = requests.patch(url, headers=headers, auth=self._authentication, json=json)

        # --- Handle response ---
        if response.status_code > 200 and response.status_code < 300:
            pass
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

    def create_new_activity(
            self,
            change_name: str,
            activity_template_name: str,
            start_date: str,
            end_date: str,
            request_description: str,
            assignee: str):
        url = f"{self._topdesk_url}/tas/api/operatorChangeActivities"
        headers = { "Content-Type": "application/json" }
        json = {
            "activityTemplate": activity_template_name,
            "changeId": change_name,
            "plannedStartDate": start_date,
            "plannedFinalDate": end_date,
            # "assignee": {
            #   "id": "a113342d-89b7-4c02-957c-af75c0505fd1",
            #   "groupId": "a247jedd-69b7-4cbd-9dw1-af25h5g505fd1",
            #   "type": "operator"
            # },
            "action": assignee,
            "request": request_description
        }

        response = requests.post(url, headers=headers, auth=self._authentication, json=json)

        # --- Handle response ---
        if response.status_code > 200 and response.status_code < 300:
            pass
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

    def get_asset(self, id: str):
        url = f"{self._topdesk_url}/tas/api/assetmgmt/assets/{id}"
        headers = { "Content-Type": "application/json" }

        response = requests.get(url, headers=headers, auth=self._authentication)

        # --- Handle response ---
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

    def get_change_templates(self):
        url = f"{self._topdesk_url}/tas/api/applicableChangeTemplates"
        headers = { "Content-Type": "application/json" }

        response = requests.get(url, headers=headers, auth=self._authentication)

        # --- Handle response ---
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"status: {response.status_code}, error: {response.text}")

########################################################################################################################

class ChangeTicket:
    def __init__(self, json_data: dict):
        # extract required data
        self.id             = json_data.get('number')
        self.requester      = json_data.get('requester').get('name')
        self.branch         = json_data.get('branch').get('name')
        self.location       = json_data.get('location').get('name')
        self.template_number = self.get_number_of_template_with_id(json_data.get('templateId'))

        results = ApiService().get_change_request(endpoint=json_data.get('requests')).get('results')

        if len(results) != 1:
            raise Exception("Multiple results, not sure what to choose.")
        request = results[0].get('memoText')

        if not request or request == '':
            raise Exception("Empty request, not possible to proceed.")

        request = self.parse_memo_text_to_dict(request)

        self.email                      = request.get( 'Email' )
        self.personal_phone_number      = request.get( 'Personal phone number (Ex. +45xxxxxxxx)' )
        self.date_of_birth              = self.convert_topdesk_date_to_datetime(request.get( 'Date of birth' ))
        self.start_date                 = self.convert_topdesk_date_to_datetime(request.get( 'Start date' ))
        self.end_date                   = self.convert_topdesk_date_to_datetime(request.get( 'End date' ))
        self.manager                    = request.get( 'Manager' )
        self.ec_email                   = request.get( '(EC) Email' )
        self.ec_personal_phone_number   = request.get( '(EC) Personal phone number (Ex. +45xxxxxxxx)' )

        errors = ChangeValidator().validate(change_ticket=self)

        self.as_dictionary = request
        self.as_dictionary['Number'] = self.id
        self.as_dictionary['Requester'] = self.requester
        self.as_dictionary['Branch'] = self.branch
        self.as_dictionary['Location'] = self.location
        self.as_dictionary['Template Number'] = self.template_number

        # reject if there are errors, approve otherwise
        if len(errors) > 0:
            error_message = "Please re-submit the form with valid data or contact Servicedesk!\n\n" + ", ".join(errors)
            ApiService().reject_change(self.id, error_message)
            raise Exception(error_message)
        else:
            ApiService().approve_change(self.id)

    def convert_topdesk_date_to_datetime(self, dt: str):
        if dt is None or dt == "":
            return None
        else:
            return datetime.strptime(dt, "%B %d, %Y").date()

    def parse_memo_text_to_dict(self, memo_text: str) -> dict:
        # Split the text by <br/><br/>
        fields = memo_text.split('<br/><br/>')
        result = {}

        for field in fields:
            # Match label and value: Label<br/>- Value
            parts = field.split('<br/>- ')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                result[key] = value
        return result

    def get_number_of_template_with_id(self, template_id):
        all_available_templates = ApiService().get_change_templates().get("results")
        for template in all_available_templates:
            if template.get('id') == template_id:
                return template.get('number')
        return None

########################################################################################################################

class ChangeValidator():
    def validate(self, change_ticket: ChangeTicket):
        errors = []

        # validate personal email address
        if change_ticket.email is not None and not self.is_valid_email(change_ticket.email):
            errors.append("Invalid email address.")

        # validate emergency contact personal email address
        if change_ticket.ec_email is not None and not self.is_valid_email(change_ticket.ec_email):
            errors.append("Invalid emergency contact email address.")

        # validate personal phone number
        if (change_ticket.personal_phone_number is not None
                and not self.is_valid_phone_number(change_ticket.personal_phone_number)):
            errors.append("Invalid phone number.")

        # validate emergency contact personal phone number
        if (change_ticket.ec_personal_phone_number is not None
                and not self.is_valid_phone_number(change_ticket.ec_personal_phone_number)):
            errors.append("Invalid emergency contact phone number.")

        # validate if the supplied manager exists and it is unique
        if change_ticket.manager is not None:
            found, matches = self.is_valid_manager(change_ticket.manager)
            if not found:
                if not matches:
                    errors.append("Manager not found.")
                else:
                    matches_as_str = ", ".join(matches)
                    errors.append(f"Found multiple matches for the manager you submitted: {matches_as_str}")

        today = date.today()
        # validate date of birth is less than today
        if change_ticket.date_of_birth is not None and change_ticket.date_of_birth >= today:
            errors.append("Employee's birth date cannot be in the future.")

        # validate start date is at least today
        if change_ticket.start_date is not None and change_ticket.start_date < today:
            errors.append("Start date cannot be in the past.")

        # validate end date is at least start date, if it exists at all
        if (change_ticket.end_date is not None
                and change_ticket.end_date is not None and change_ticket.end_date < change_ticket.start_date):
            errors.append("End date cannot be before the start date.")

        return errors

    def is_valid_email(self, email: str) -> bool:
        try:
            validate_email(email, check_deliverability=False)  # Set to True if you want DNS checks
            return True
        except EmailNotValidError:
            return False

    def is_valid_phone_number(self, phone_raw: str):
        # First try parsing with no region (only works if it starts with '+')
        try:
            number = phonenumbers.parse(phone_raw, None)
            if phonenumbers.is_possible_number(number) and phonenumbers.is_valid_number(number):
                return True
        except NumberParseException:
            pass

        return False

    def is_valid_manager(self, name: str) -> Tuple[bool, Union[dict, list, None]]:
        results = ApiService().lookup_manager(name=name).get('results', [])

        if len(results) == 1:
            return True, results[0]
        elif len(results) == 0:
            return False, None
        else:
            return False, [r['name'] for r in results]

########################################################################################################################

class OnboardingSettings:
    def __init__(self):
        self.global_settings    = {}
        self.widgets            = {}

        self.onboarding_settings_asset = ApiService().get_asset(
            id="625d58ac-8042-4478-93cf-a72b02336896") # Onboarding Settings Asset

        self.set_global_settings()
        self.set_widgets()

    def get_activities_for_change_template(self, change_template_number):
        country = self.global_settings.get(change_template_number)
        widget = self.widgets.get(country)

        return self.onboarding_settings_asset.get('data').get(widget)

    def set_global_settings(self):
        global_settings_entries = self.onboarding_settings_asset.get("data").get(
            "@gridwidgetfield_961c1302-cf93-4104-9f97-3604fff406e6")

        for entry in global_settings_entries:
            global_settings_entry = ApiService().get_asset(id=entry)

            country = global_settings_entry.get("data").get("country")
            change_template = global_settings_entry.get("data").get("change-template")
            self.global_settings[change_template] = country

    def set_widgets(self):
        widgets_as_dict = {}
        widgets = self.onboarding_settings_asset.get("metadata").get("template").get("tabs")[0].get("columns")[1].get(
            "widgets")
        for widget in widgets:
            widgets_as_dict[widget.get("title")] = widget.get("fieldId")

        self.widgets = widgets_as_dict

########################################################################################################################

class ActivityGenerator():
    def generate_activities_for_change(self, change_ticket: ChangeTicket):
        templates = OnboardingSettings().get_activities_for_change_template(change_ticket.template_number)

        for template in templates:
            settings = ApiService().get_asset(id=template) #  DK entry

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

########################################################################################################################
#################################################### START OF SCRIPT ###################################################

parser = AzureWebhookParser()
change_id = parser.parse_webhook()

Configuration()
apiService = ApiService()

change_ticket = apiService.get_change(id=change_id)
change_ticket = ChangeTicket(change_ticket)

# should no Exceptions be raised until this point, the change must be approved and ready to be processed
ActivityGenerator().generate_activities_for_change(change_ticket)

######################################################### END ##########################################################