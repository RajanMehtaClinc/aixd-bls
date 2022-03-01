import werkzeug

from date_webhook.fulfillments import (
    passthrough,
    balance_fulfillment,
    identity_verification_fulfillment,
    increase_cc_limit_fulfillment,
    outofscope_fulfillment,
)


class NotFulfilledException(werkzeug.exceptions.HTTPException):
    code = 501
    description = "state and intent combination does not have a fulfiller"


def ignore(request):
    pass


def panic(request):
    raise NotFulfilledException(
        description=f""
        f"state: [{request.get_state()}] + "
        f"intent: [{request.get_intent()}] "
        f"combination does not have a fulfiller"
    )


FULFILLMENTS = {
    "get_balance": {
        "get_balance_start": balance_fulfillment.handle,
        "cs_yes": balance_fulfillment.handle,
    },
    "identity_verification": {
        "get_balance_start": identity_verification_fulfillment.handle,
    },
    "confirm_details": {"cs_yes": identity_verification_fulfillment.handle,},
    "increase_cc_limit": {
        "increase_cc_limit_start": increase_cc_limit_fulfillment.handle,
        "ambiguous_amount_start": increase_cc_limit_fulfillment.handle_ambiguous,
    },
    "*": passthrough.handle,
}


def fulfill(request):
    preprocess(request)
    state = request.get_state()
    intent = request.get_intent()
    print("state: ", state)
    print("intent: ", intent)
    if state in FULFILLMENTS:
        if intent in FULFILLMENTS[state]:
            print(f"Calling fulfiller [{state}][{intent}]")
            return FULFILLMENTS[state][intent](request)
        elif "*" in FULFILLMENTS[state]:
            print(f"Calling fulfiller [{state}][*]")
            return FULFILLMENTS[state]["*"](request)
    print(f"Calling fulfiller [*]")
    return FULFILLMENTS["*"](request)


def preprocess(request):
    pass
