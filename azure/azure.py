import sys
import re
from abc import ABC, abstractmethod
import automationassets
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

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

        self.fullname                   = request.get( 'Full name' )
        self.email                      = request.get( 'Email' )
        self.personal_phone_number      = request.get( 'Personal phone number (Ex. +45xxxxxxxx)' )
        self.address                    = request.get( 'Address' )
        self.date_of_birth              = self.convert_topdesk_date_to_datetime(request.get( 'Date of birth' ))
        self.cpr                        = request.get( 'CPR number' )
        self.department                 = request.get( 'Department' )
        self.employee_type              = request.get( 'Employee type' )
        self.job_title                  = request.get( 'Job title' )
        self.start_date                 = self.convert_topdesk_date_to_datetime(request.get( 'Start date' ))
        self.end_date                   = self.convert_topdesk_date_to_datetime(request.get( 'End date' ))
        self.manager                    = request.get( 'Manager' )
        self.hire_reason                = request.get( 'Hire reason' )
        self.ORDER_ACCESS_KEYS          = request.get( 'Order access keys?' )
        self.ORDER_WELCOME_PRESENT      = request.get( 'Order welcome present?' )
        self.ec_fullname                = request.get( '(EC) Full name' )
        self.ec_email                   = request.get( '(EC) Email' )
        self.ec_personal_phone_number   = request.get( '(EC) Personal phone number (Ex. +45xxxxxxxx)' )

        errors = change_validator.validate(self)

        self.as_dictionary = request
        self.as_dictionary['Number'] = self.id
        self.as_dictionary['Requester'] = self.requester
        self.as_dictionary['Branch'] = self.branch
        self.as_dictionary['Location'] = self.location
        self.as_dictionary['Template Number'] = self.template_number

        # reject if there are errors, approve otherwise
        # if len(errors) > 0:
        #     error_message = "Please re-submit the form with valid data or contact Servicedesk!\n\n" + ", ".join(errors)
        #     ApiService().reject_change(self.id, error_message)
        #     raise Exception(error_message)
        # else:
        #     ApiService().approve_change(self.id)

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
###################### START OF SCRIPT #################################################################################
parser = AzureWebhookParser()
change_id = parser.parse_webhook()

# change_id = "C 2512-0012"

Configuration()
apiService = ApiService()

change_ticket = apiService.get_change(id=change_id)
change_ticket = ChangeTicket(change_ticket)

# should no Exceptions be raised until this point, the change must be approved and ready to be processed
ActivityGenerator().generate_activities_for_change(change_ticket)

############################ END #######################################################################################