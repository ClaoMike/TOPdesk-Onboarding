from AzureWebhookParser import AzureWebhookParser
from Configuration import Configuration
from ApiService import ApiService
from ChangeTicket import ChangeTicket

###################### START OF SCRIPT ######################
parser = AzureWebhookParser()
# change_id = parser.parse_webhook()

change_id = "C 2510-0087"

Configuration()
apiService = ApiService()

change_ticket = apiService.get_change(id=change_id)
change_ticket = ChangeTicket(change_ticket)


############################ END ############################