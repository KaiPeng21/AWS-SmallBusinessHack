"""
Example Lambda Function That Interfaces with Amazon Lex
"""

from esclient import SBADocument
from client_lex import LexResponse, to_validate_text
from config import ES_HOST, ES_PORT
from client_comprehend import detect_keyphrases

import json

sbadoc = SBADocument(host=ES_HOST, port=ES_PORT)

def validate_slots(slots : dict) -> dict:
    """ Validate slots
    Arguments:
        slots {dict} -- slots dictionary to be validate
    Returns:
        dict -- validated version
    """

    #slots["ESMLFileTypes"] = to_validate_text(slots.get("ESMLFileTypes"), ["text", "image"])

    return slots

def make_response(event : dict):

    invocation_source = event["invocationSource"]
    assert invocation_source == "DialogCodeHook"

    session_attributes = event["sessionAttributes"]
    bot_name = event["bot"]["name"]
    current_intent = event["currentIntent"]["name"]
    intent_slots = validate_slots(event["currentIntent"]["slots"])

    print(f"Processing bot {bot_name} intent {current_intent}...")

    lex_resp = LexResponse(
        session_attribute=session_attributes,
        intent_name=current_intent,
        slots=intent_slots
    )

    if intent_slots.get("SBADescription") is None:
        return lex_resp.response_elicit_slot(
            slot_to_elicit="SBADescription",
            message_content="Would you give a some description about your business plan?"
        )

    keyphrases = detect_keyphrases(text=intent_slots.get("SBADescription"))
    if len(keyphrases) == 0:
        keyphrases = intent_slots.get("SBADescription").split()
    res = sbadoc.search_document_by_keywords(keywords=keyphrases, num_of_docs=5).json()

    data_list = [hit["_source"] for hit in res["hits"]["hits"]]

    resp = lex_resp.response_close(
        success=True,
        message_content=f"Here are some information about your business success plan!",
        generic_attachments=[
            lex_resp.create_generic_attachment(
                title=data["company"],
                sub_title=f'Success Rate: {round(data["probability"], 2)}, Awards: ${data["award"]}'[:50],
            )
            for data in data_list
        ]
    )
    print(resp)
    return resp  

def lambda_handler(event : dict, context : dict) -> dict:
    """[summary]
    
    Arguments:
        event {dict} -- [description]
        context {dict} -- [description]
    
    Returns:
        dict -- [description]
    """

    print(f"lex-hook-event: {event}")

    try:
        return make_response(event)
    except Exception as e:
        print(e)
        return LexResponse().response_close(
            success=False,
            message_content=f"Sorry! An error occur {e}"
        )

if __name__=="__main__":
    lambda_handler({}, {})