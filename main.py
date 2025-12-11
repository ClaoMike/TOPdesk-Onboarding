from AzureWebhookParser import AzureWebhookParser
from Configuration import Configuration
from ApiService import ApiService
from ChangeTicket import ChangeTicket
from ActivityGenerator import ActivityGenerator

###################### START OF SCRIPT ######################
parser = AzureWebhookParser()
# change_id = parser.parse_webhook()

change_id = "C 2512-0043"

Configuration()
apiService = ApiService()

change_ticket = apiService.get_change(id=change_id)
change_ticket = ChangeTicket(change_ticket)

# should no Exceptions be raised until this point, the change must be approved and ready to be processed
ActivityGenerator().generate_activities_for_change(change_ticket)

############################ END ############################