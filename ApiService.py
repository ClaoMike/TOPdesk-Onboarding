from Singleton import Singleton

import requests
from requests.auth import HTTPBasicAuth

class ApiService(Singleton):
    _topdesk_url = "https://dlfseeds.topdesk.net"
    _authentication = HTTPBasicAuth(USERNAME, PASSWORD)

    def get_change(self, name: str):
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{self._topdesk_url}/tas/api/operatorChanges/{name}",
            headers=headers,
            auth=self._authentication
        )
        # --- Handle response ---
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve change:", response.status_code, response.text)
            return None

    def get_change_request(self, endpoint: str):
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{self._topdesk_url}{endpoint}",
            headers=headers,
            auth=self._authentication
        )
        # --- Handle response ---
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve change:", response.status_code, response.text)
            return None

    def lookup_manager(self, name: str):
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{self._topdesk_url}/tas/api/persons/lookup?name={name}",
            headers=headers,
            auth=self._authentication
        )
        # --- Handle response ---
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve change:", response.status_code, response.text)
            return None

    def reject_change(self, identifier: str, message: str):
        default_message = "Please re-submit the form with valid data or contact Servicedesk!"
        joined_message = '\n'.join(message)
        joined_message += '\n\n' + default_message

        headers = {
            "Content-Type": "application/json-patch+json"
        }

        json = [
            {
                "op": "add",
                "path": "/progressTrail",
                "value": joined_message
            },
            {
                "op": "replace",
                "path": "/status",
                "value": "rejected"
            }

        ]

        response = requests.patch(
            f"{self._topdesk_url}/tas/api/operatorChanges/{identifier}",
            headers=headers,
            auth=self._authentication,
            json=json
        )
        # --- Handle response ---
        if response.status_code > 200 and response.status_code < 300:
            pass
        else:
            print("Failed to retrieve change:", response.status_code, response.text)

    def approve_change(self, identifier: str):
        headers = {
            "Content-Type": "application/json-patch+json"
        }

        json = [
            {
                "op": "replace",
                "path": "/status",
                "value": "approved"
            }

        ]

        response = requests.patch(
            f"{self._topdesk_url}/tas/api/operatorChanges/{identifier}",
            headers=headers,
            auth=self._authentication,
            json=json
        )
        # --- Handle response ---
        if response.status_code > 200 and response.status_code < 300:
            pass
        else:
            print("Failed to retrieve change:", response.status_code, response.text)

    def send_email(self, data: dict, details: dict):
        headers = {
            "Content-Type": "application/json"
        }

        json = {
            "from": "servicedesk@dlf.com",
            "to": "claudiu.jechel@dlf.com",
            # "cc": "",
            # "bcc": "",
            "subject": "Onboarding",
            "body": generate_email_body(
                branch_name="DLF HQ",
                change_id=CHANGE_ID,
                manager_name="Claudiu Mihai Jechel",
                activity_message=compose_email(data, details)
            ),
            "isHtmlBody": "true"
        }

        response = requests.post(
            f"{self._topdesk_url}/services/email-v1/api/send",
            headers=headers,
            auth=self._authentication,
            json=json
        )

        # --- Handle response ---
        if response.status_code == 202:
            pass
        else:
            print("Failed to send the email:", response.status_code, response.text)

    def create_new_activity(self, change_name: str, activity_template_name: str, start_date: str, end_date: str,
                            request_description: str):
        headers = {
            "Content-Type": "application/json"
        }

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
            # "status": "Planned",
            "request": request_description,
        }

        response = requests.post(
            f"{self._topdesk_url}/tas/api/operatorChangeActivities",
            headers=headers,
            auth=self._authentication,
            json=json
        )
        # --- Handle response ---
        if response.status_code > 200 and response.status_code < 300:
            pass
        else:
            print("Failed to retrieve change:", response.status_code, response.text, response)