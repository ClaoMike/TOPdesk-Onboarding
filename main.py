from AzureWebhookParser import AzureWebhookParser
from Configuration import Configuration
from ApiService import ApiService

###################### START OF SCRIPT ######################
parser = AzureWebhookParser()
# change_id = parser.parse_webhook()

change_id = "C 2510-0087"

Configuration()
apiService = ApiService()

change_ticket = apiService.get_change(id=change_id)
print(change_ticket)
# submitted_data = extract_data(change=change_ticket)
# is_valid_request, errors = validate_submitted_data(submitted_data) # validate the data
#
# if is_valid_request:
#     approve_change(id=change_id)
#     create_activities(change_id=change_id, data=submitted_data)
# else:
#     reject_change(CHANGE_ID, errors)
############################ END ############################