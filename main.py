###################### START OF SCRIPT ######################
# change_id = parse_webhook_data()
change_id = "I 0000-0000"

change_ticket = get_change_ticket(id=change_id)
submitted_data = extract_data(change=change_ticket)
is_valid_request, errors = validate_submitted_data(submitted_data) # validate the data

if is_valid_request:
    approve_change(id=change_id)
    create_activities(change_id=change_id, data=submitted_data)
else:
    reject_change(CHANGE_ID, errors)
############################ END ############################