from date_webhook.utils.payload import Payload


def handle(request: Payload):
    rb = request.get()

    if "_PERSON_NAME_" in rb["slots"] and "_PHONE_NUMBER_" in rb["slots"]:
        rb["session_info"]["is_authenticated"] = True
        rb["session_info"]["mufg_user_id"] = 123456

    if "_INITIAL_INTENT_" in rb["slots"]:
        if rb["slots"]["_INITIAL_INTENT_"]["values"][0]["value"] == "get balance":
            rb["state"] = "get_balance"

    request.overwrite(rb)
