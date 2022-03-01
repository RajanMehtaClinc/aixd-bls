from date_webhook.utils.payload import Payload


def handle(request: Payload):
    rb = request.get()
    if "is_authenticated" not in rb.get("session_info"):
        rb["session_info"]["is_authenticated"] = False
        rb["state"] = "identity_verification"
    else:
        if rb.get("session_info", {}).get("is_authenticated"):
            rb["slots"]["_BALANCE_"] = {
                "type": "string",
                "values": [
                    {
                        "status": "CONFIRMED",
                        "tokens": "2000.00",
                        "value": "2000.00",
                        "currency": "dollars",
                    }
                ],
            }

    # Blind resolve slots
    for slot in rb["slots"]:
        for slot_value in rb["slots"][slot]["values"]:
            if "status" in slot_value:
                slot_value["status"] = "CONFIRMED"
            else:
                slot_value["resolved"] = 1
            if "value" not in slot_value:
                slot_value["value"] = slot_value["tokens"]

    # Save intent in a slot
    rb["slots"]["_INITIAL_INTENT_"] = {
        "type": "string",
        "values": [
            {"status": "CONFIRMED", "tokens": "get balance", "value": "get balance"}
        ],
    }

    request.overwrite(rb)
