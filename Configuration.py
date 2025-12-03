from Singleton import Singleton
import automationassets

class Configuration(Singleton):
    def _init_singleton(self):
        cred = automationassets.get_automation_credential("CREDENTIAL_TOPDESK_API")
        self.USERNAME = cred.get("username")
        self.PASSWORD = cred.get("password")