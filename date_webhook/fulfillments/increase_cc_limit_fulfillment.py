from date_webhook.utils.payload import Payload


def handle(request: Payload):
    rb = request.get()

    # Blind resolve all slots
    for slot in rb["slots"]:
        for slot_value in rb["slots"][slot]["values"]:
            if "status" in slot_value:
                slot_value["status"] = "CONFIRMED"
            else:
                slot_value["resolved"] = 1
            if "value" not in slot_value:
                slot_value["value"] = slot_value["tokens"]

    request.overwrite(rb)


def handle_ambiguous(request: Payload):
    rb = request.get()

    # Blind resolve all slots
    for slot in rb["slots"]:
        for slot_value in rb["slots"][slot]["values"]:
            if "status" in slot_value:
                slot_value["status"] = "CONFIRMED"
            else:
                slot_value["resolved"] = 1
            if "value" not in slot_value:
                slot_value["value"] = slot_value["tokens"]

    # special case of ambiguous slot: ambiguous_amount_start
    if rb["intent"] == "ambiguous_amount_start":
        if request.slot_exists("ambiguous_amount"):
            if not request.slot_exists("annual_income"):
                # create annual income slot. copy ambiguous-amount-slot to annual-income-slot
                rb["slots"]["_ANNUAL_INCOME_"] = {
                    "type": "string",
                    "values": [
                        {
                            "status": "CONFIRMED",
                            "tokens": rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0][
                                "tokens"
                            ],
                            "value": rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0][
                                "value"
                            ],
                            "currency": "dollars",
                        }
                    ],
                }
                # Now, delete ambiguous-amount-slot
                rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0]["status"] = "DELETE"

            elif request.slot_exists("annual_income") and not request.slot_exists(
                "estimate_amount"
            ):
                rb["slots"]["_ESTIMATE_AMOUNT_"] = {
                    "type": "string",
                    "values": [
                        {
                            "status": "CONFIRMED",
                            "tokens": rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0][
                                "tokens"
                            ],
                            "value": rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0][
                                "value"
                            ],
                            "currency": "dollars",
                        }
                    ],
                }
                rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0]["status"] = "DELETE"

            elif (
                request.slot_exists("annual_income")
                and request.slot_exists("estimate_amount")
                and not request.slot_exists("desired_limit")
            ):
                rb["slots"]["_DESIRED_LIMIT_"] = {
                    "type": "string",
                    "values": [
                        {
                            "status": "CONFIRMED",
                            "tokens": rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0][
                                "tokens"
                            ],
                            "value": rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0][
                                "value"
                            ],
                            "currency": "dollars",
                        }
                    ],
                }
                rb["slots"]["_AMBIGUOUS_AMOUNT_"]["values"][0]["status"] = "DELETE"

    # Similarly, you can add special case of of ambiguous slot: ambiguous_amount_update

    # if all three money slots present -> copy ambiguous amount to desired_limit -> delete ambiguous amount
    # if only two money slots present -> copy ambiguous amount to estimate_amount -> delete ambiguous amount
    # if only one money slot present -> copy ambiguous amount to annual_income -> delete ambiguous amount

    request.overwrite(rb)
