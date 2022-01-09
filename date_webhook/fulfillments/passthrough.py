from date_webhook.utils.payload import Payload


def handle(request: Payload):
    rb = request.get()

    # Blind resolve slots
    for slot in rb["slots"]:
        for slot_value in rb["slots"][slot]["values"]:
            if "status" in slot_value:
                slot_value["status"] = "CONFIRMED"
            else:
                slot_value["resolved"] = 1
            if "value" not in slot_value:
                slot_value["value"] = slot_value["tokens"]

    request.overwrite(rb)
