import change_validator
from ApiService import ApiService

from datetime import datetime

class ChangeTicket:
    def __init__(self, json_data: dict):
        # extract required data
        self.id         = json_data.get('number')
        self.requester  = json_data.get('requester').get('name')
        self.branch     = json_data.get('branch').get('name')
        self.location   = json_data.get('location').get('name')

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
        # TBR
        # self.ORDER_HARDWARE             = request.get( 'Order hardware?' )
        # self.DESCRIBE                   = request.get( 'Describe' )
        # self.ORDER_MASTERCARD           = request.get( 'Order Mastercard?' )
        # self.ORDER_COMPANY_VEHICLE      = request.get( 'Order company vehicle?' )
        self.ORDER_ACCESS_KEYS          = request.get( 'Order access keys?' )
        self.ORDER_WELCOME_PRESENT      = request.get( 'Order welcome present?' )
        self.ec_fullname                = request.get( '(EC) Full name' )
        self.ec_email                   = request.get( '(EC) Email' )
        self.ec_personal_phone_number   = request.get( '(EC) Personal phone number (Ex. +45xxxxxxxx)' )

        errors = change_validator.validate(self)

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
