from date_webhook.utils.payload import Payload


def handle(request: Payload):
    rb = request.get()

    """
    # create a business logic transition from root -> get_balance
    # then enable business logic for outofscope on settings page
    # below line updates the state and hence makes a business logic transition
      to get_balance when an utterance goes outofscope
    """
    rb["state"] = "get_balance"

    request.overwrite(rb)
