from date_webhook.utils.payload import Payload
import json

   
def handle_root(response):
    print("root")
    if response.get("classified_segments"):
        print(response["classified_segments"])
        response = prioritize_multi_intent(response)
    return response
   
def handle_bls_trans(response):
    response["state"] = "bls_transition_dest"
    return response
   
def handle_bls_terminal_states(response):
    response["terminal_states"] = {"bls_terminal": True, "bls_non_terminal": False}
    return response
   
def get_balance(response):
    print("get_balance")
    accounts = {"trading": 20000, "spend": 42, "saving": 12000, "当座": 20000}
    for slot in response["slots"].values():
        for sub_slot in slot["values"]:
            sub_slot["status"] = "CONFIRMED"
            sub_slot["value"] = sub_slot.get("value", sub_slot.get("tokens"))
    response["slots"]["_BALANCE_"] = {
                    "type": "int",
                    "values": [
                    {
                        "status": "CONFIRMED",
                        "value": accounts.get(response["slots"]["_ACC_TYPE_"]["values"][0]["tokens"]),
                    }
                    ]
                }
    return response
   
def prioritize_multi_intent(response):
    segments = {state: utterance for utterance, state in response["classified_segments"]}
    print("Segments")
    print(segments)

    goal_states = ["get_balance", "clean_hello", "clean_goodbye", "funds_transfer"]

    ordered = []
    for state in goal_states:
        if segments.get(state):
            print("Appending segment utterance")
            ordered.append(segments.get(state))

    if all(ordered):
        response["ordered_segments"] = ordered
    else:
        print("Failed to validate ordered segments")

    print("response segments")
    print(response["ordered_segments"])

    return response
   

def funds_transfer(response):
    print("funds_transfer")
    for slot in response["slots"].values():

        sub_slot = slot["values"][-1]
        sub_slot["status"] = "CONFIRMED"
        sub_slot["value"] = sub_slot.get("value", sub_slot.get("tokens"))
        slot["values"] = [sub_slot]

    # if response.get("slot_relations"):
    #     sr = response["slot_relations"]
    #     try:
    #         if int(response["slots"]["_MONEY_"]['values'][-1]['value']) > 10000:
    #                 overdraw = {
    #                         "type": "boolean",
    #                         "values": [
    #                         {
    #                             "status": "CONFIRMED",
    #                             "value": True,
    #                         }
    #                         ]
    #                     }
    #                 response['slots']['_OVERDRAW_'] = overdraw
    #         else:
    #             response['slots']['_OVERDRAW_'] = {
    #                 "type": "boolean",
    #                 "values": [
    #                 {
    #                     "status": "CONFIRMED",
    #                     "value": False,
    #                 }
    #                 ]
    #             }
    #     except:
    #         pass

    #     for value in sr:
    #         if value["source"]["slot"] == "_SOURCE_ACCOUNT_":
    #             account_num = {
    #                     "type": "string",
    #                     "values": [
    #                     {
    #                         "value": value["destination"]["value"],
    #                         "status": "CONFIRMED"
    #                     }
    #                     ]
    #                 }
    #             response['slots']['_SOURCE_ACCOUNT_NUM_'] = account_num
    #             if "checking" in value["source"]["value"]:
    #                 response['slots']['_OVERDRAW_'] = {
    #                     "type": "boolean",
    #                     "values": [
    #                     {
    #                         "status": "CONFIRMED",
    #                         "value": False,
    #                     }
    #                     ]
    #                 }

    #         if value["source"]["slot"] == "_DESTINATION_ACCOUNT_":
    #             account_num = {
    #                     "type": "string",
    #                     "values": [
    #                     {
    #                         "value": value["destination"]["value"],
    #                         "status": "CONFIRMED"
    #                     }
    #                     ]
    #                 }
    #             response['slots']['_DESTINATION_ACCOUNT_NUM_'] = account_num

    #     if response["slots"].get("_ACCT_NUM_"):
    #         for sub_slot in response["slots"]["_ACCT_NUM_"]['values']:
    #             sub_slot['status'] = 'DELETE'

    return response
   
def handle_slot_mapper(response):
    candidates = [
        {
            "value": "saving",
            "account_id": "155243",
            "balance": "4521.10",
            "currency": "USD",
        },
        {
            "value": "checking",
            "account_id": "7725485",
            "balance": "332.21",
            "currency": "USD",
        },
        {
            "value": "IRA",
            "account_id": "2938429",
            "balance": "5454.23",
            "currency": "USD",
        },
    ]
   
    mappings = [
                {
                    "type": "contextual_phrase_embedder",
                    "threshold": 0.6,
                    "values": {
                        "saving": ["saving"],
                        "checking": ["checking"],
                        "IRA": ["IRA"]
                    }
                }
            ]
    for slot in response["slots"].copy():
       
        if response["slots"][slot]['values'][0]['status'] == 'EXTRACTED':
            response["slots"][slot]['candidates'] = candidates
            response["slots"][slot]['mappings'] = mappings
   
        elif response["slots"][slot]['values'][0]['status'] == 'MAPPED':
            for candidate in candidates:
                if candidate['value'] == response["slots"][slot]['values'][0]['value']:
                    response["slots"][slot]['values'][0]['status'] = 'CONFIRMED'
    return response


def handle(request: Payload):
    rb = request.get()

    state_functions = {
        "root": handle_root,
        "acct_get_balance": get_balance,
        "acc_transfer": funds_transfer,
        "prioritize_multi_intent": handle_root,
        "bls_transition_source": handle_bls_trans,
        "bls_terminal": handle_bls_terminal_states,
        "bls_non_terminal": handle_bls_terminal_states,
        "slot_mapper_state": handle_slot_mapper,
    }

    state = request.get_state()
    print("##### state: ", state)

    handler = state_functions.get(state)
    if handler:
        response = handler(rb)
    else:
        response = rb

    # Blind resolve slots
    for slot in rb["slots"]:
        for slot_value in rb["slots"][slot]["values"]:
            if "status" in slot_value:
                slot_value["status"] = "CONFIRMED"
            else:
                slot_value["resolved"] = 1
            if "value" not in slot_value:
                slot_value["value"] = slot_value["tokens"]

    print("##### FINAL RESPONSE #####")
    print(json.dumps(response))

    request.overwrite(rb)
