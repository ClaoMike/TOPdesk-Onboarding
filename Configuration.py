from Singleton import Singleton

from dotenv import load_dotenv
import os
# import automationassets

class Configuration(Singleton):
    _initialized = False

    USERNAME = ""
    PASSWORD = ""

    def __init__(self):
        if not self._initialized:
            _initialized = True

            # DEVELOPMENT
            load_dotenv()

            self.USERNAME = os.getenv("USERNAME")
            self.PASSWORD = os.getenv("PASSWORD")

            # PRODUCTION
            # cred = automationassets.get_automation_credential("TOPDESK_API_ACCOUNT")
            # USERNAME = cred["username"]
            # PASSWORD = cred["password"]