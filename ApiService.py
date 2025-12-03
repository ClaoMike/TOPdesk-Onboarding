from Exceptions import InvalidInputData, NoPermission, NotFound
from Singleton import Singleton
from Configuration import Configuration

import requests
from requests.auth import HTTPBasicAuth

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
