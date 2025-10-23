from ApiService import ApiService

import phonenumbers
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError
from typing import Tuple, Union
from datetime import date
import ChangeTicket

def validate(change_ticket: ChangeTicket):
    errors = []

    # validate personal email address
    if not is_valid_email(change_ticket.email):
        errors.append("Invalid email address.")

    # validate emergency contact personal email address
    if not is_valid_email(change_ticket.ec_email):
        errors.append("Invalid emergency contact email address.")

    # validate personal phone number
    if not is_valid_phone_number(change_ticket.personal_phone_number):
        errors.append("Invalid phone number.")

    # validate emergency contact personal phone number
    if not is_valid_phone_number(change_ticket.ec_personal_phone_number):
        errors.append("Invalid emergency contact phone number.")

    # validate if the supplied manager exists and it is unique
    found, matches = is_valid_manager(change_ticket.manager)
    if not found:
        if not matches:
            errors.append("Manager not found.")
        else:
            matches_as_str = ", ".join(matches)
            errors.append(f"Found multiple matches for the manager you submitted: {matches_as_str}")

    today = date.today()
    # validate date of birth is less than today
    if change_ticket.date_of_birth >= today:
        errors.append("Employee's birth date cannot be in the future.")

    # validate start date is at least today
    if change_ticket.start_date < today:
        errors.append("Start date cannot be in the past.")

    # validate end date is at least start date, if it exists at all
    if change_ticket.end_date is not None and change_ticket.end_date < change_ticket.start_date:
        errors.append("End date cannot be before the start date.")

    return errors

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)  # Set to True if you want DNS checks
        return True
    except EmailNotValidError:
        return False


def is_valid_phone_number(phone_raw: str):
    # First try parsing with no region (only works if it starts with '+')
    try:
        number = phonenumbers.parse(phone_raw, None)
        if phonenumbers.is_possible_number(number) and phonenumbers.is_valid_number(number):
            return True
    except NumberParseException:
        pass

    return False


def is_valid_manager(name: str) -> Tuple[bool, Union[dict, list, None]]:
    results = ApiService().lookup_manager(name=name).get('results', [])

    if len(results) == 1:
        return True, results[0]
    elif len(results) == 0:
        return False, None
    else:
        return False, [r['name'] for r in results]