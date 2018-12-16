""" 
A module that interfaces with Amazon Lex
"""
from difflib import SequenceMatcher

class LexResponse:

    def __init__(self, session_attribute : dict = {}, intent_name : str = "", slots : dict = {}):
        self.session_attribute = session_attribute
        self.intent_name = intent_name
        self.slots = slots

        self._support_content_types = ["PlainText", "SSML", "CustomPayload"]

    def create_button(self, text : str, value : str) -> dict:
        """ Create a chatbot button
        
        Arguments:
            text {str} -- button text label
            value {str} -- value sent to server on button click
        
        Returns:
            dict -- dictionary of button
        """
        return {
            "text" : text,
            "value" : value
        }

    def create_generic_attachment(self, title : str = None, sub_title : str = None, image_url : str = None, attachment_link_url : str = None, buttons : list = None) -> dict:
        """ Create a generic attachment dictionary, an option rendered to the user when a prompt is shown.
        Can be an image, a button, or text.
        
        Keyword Arguments:
            title {str} -- attachment title (default: {None})
            sub_title {str} -- attachment subtitle (default: {None})
            image_url {str} -- image url (default: {None})
            attachment_link_url {str} -- link url (default: {None})
            buttons {list} -- list of buttons (default: {None})
        
        Returns:
            dict -- generic attachment dictionary
        """
        attachment = {}
        if title is not None:
            attachment["title"] = title
        if sub_title is not None:
            attachment["subTitle"] = sub_title
        if image_url is not None:
            attachment["imageUrl"] = image_url
        if attachment_link_url is not None:
            attachment["attachmentLinkUrl"] = attachment_link_url
        if buttons is not None:
            attachment["buttons"] = buttons
        return attachment
    
    def make_options(self, buttons : list) -> dict:
        """ Create a list of buttons
        
        Arguments:
            buttons {list} -- list of button dictionaries
        
        Returns:
            dict -- generic attachment dictionary
        """
        return self.create_generic_attachment(
            buttons=buttons
        )

    def response_close(self, success : bool, message_content : str, content_type : str = "PlainText", generic_attachments : list = None) -> dict:
        """ Informs Amazon Lex not to expect a response from the user.
        E.g. Your pizza order has been placed.
        
        Arguments:
            success {bool} -- Fulfilled or Failed
            message_content {str} -- Message to convey to the user
        Keyword Arguments:
            content_type {str} -- PlainText or SSML or CustomPayload (default: {"PlainText"})
            generic_attachments {list} -- Optional list of generic attachment dictionary (default: {None})
        
        Returns:
            dict -- response to lex
        """
        assert content_type in self._support_content_types
        response = {
            "sessionAttributes" : self.session_attribute,
            "dialogAction" : {
                "type" : "Close",
                "fulfillmentState" : "Fulfilled" if success else "Failed",
                "message" : {
                    "contentType" : content_type,
                    "content" : message_content
                }
            }
        }
        if generic_attachments:
            response["dialogAction"]["responseCard"] = {
                "version" : 1,
                "contentType" : "application/vnd.amazonaws.card.generic",
                "genericAttachments" : generic_attachments
            }
        return response
    
    def response_confirm_intent(self, message_content : str, content_type : str = "PlainText", generic_attachments : list = None) -> dict:
        """ Informs Amazon Lex that the user is expected to give a yes or no answer to confirm or deny the current intent.
        E.g. Are you sure you want a large pizza?
        
        Arguments:
            message_content {str} -- Message to convey to the user
        Keyword Arguments:
            content_type {str} -- PlainText or SSML or CustomPayload (default: {"PlainText"})
            generic_attachments {list} -- Optional list of generic attachment dictionary (default: {None})
        
        Returns:
            dict -- response to lex
        """
        assert content_type in self._support_content_types
        response = {
            "sessionAttributes" : self.session_attribute,
            "dialogAction" : {
                "type" : "ConfirmIntent",
                "message" : {
                    "contentType" : content_type,
                    "content" : message_content
                },
                "intentName" : self.intent_name,
                "slots" : self.slots
            }
        }
        if generic_attachments:
            response["dialogAction"]["responseCard"] = {
                "version" : 1,
                "contentType" : "application/vnd.amazonaws.card.generic",
                "genericAttachments" : generic_attachments
            }
        return response
    
    def response_delegate(self, delegate_slots : dict) -> dict:
        """ Directs Amazon Lex to choose the next course of action based on teh bot configuration.
        The response must include any session attributes, and the slots field must include all of
        the slots specified for the request intent. If the value of the field is unkown, you must 
        set it to null. You will get a DependencyFailedException exception if your fulfillment 
        function returns the Delegate dialog action without removing any slots.
        
        Arguments:
            delegate_slots {dict} -- delegate slot
        Returns:
            dict -- lex response
        """
        return {
            "sessionAttributes" : self.session_attribute,
            "dialogAction" : {
                "type" : "Delegate",
                "slots" : delegate_slots
            }
        }

    def response_elicit_intent(self, message_content : str, content_type : str = "PlainText", generic_attachments : list = None) -> dict:
        assert content_type in self._support_content_types
        response = {
            "sessionAttributes" : self.session_attribute,
            "dialogAction" : {
                "type" : "ElicitIntent",
                "message" : {
                    "contentType" : content_type,
                    "content" : message_content
                }
            }
        }
        if generic_attachments:
            response["dialogAction"]["responseCard"] = {
                "version" : 1,
                "contentType" : "application/vnd.amazonaws.card.generic",
                "genericAttachments" : generic_attachments
            }
        return response
    
    def response_elicit_slot(self, 
        slot_to_elicit : str,
        message_content : str, 
        content_type : str = "PlainText", 
        generic_attachments : list = None
        ) -> dict:
        """ Informs Amazon Lex that the user is expected to provide a slot value in the response.
        
        Arguments:
            slot_to_elicit {str} -- slot to elicit
            message_content {str} -- message
        
        Keyword Arguments:
            content_type {str} -- PlainText or SSML or CustomPayload (default: {"PlainText"})
            generic_attachments {list} -- Optional list of generic attachment dictionary (default: {None})
        
        Returns:
            dict -- response to lex
        """

        assert content_type in self._support_content_types
        assert slot_to_elicit in self.slots.keys()
        response = {
            "sessionAttributes" : self.session_attribute,
            "dialogAction" : {
                "type" : "ElicitSlot",
                "message" : {
                    "contentType" : content_type,
                    "content" : message_content
                },
                "intentName": self.intent_name,
                "slots": self.slots,
                "slotToElicit" : slot_to_elicit
            }
        }
        if generic_attachments:
            response["dialogAction"]["responseCard"] = {
                "version" : 1,
                "contentType" : "application/vnd.amazonaws.card.generic",
                "genericAttachments" : generic_attachments
            }
        return response


def to_validate_text(a : str, textlist : list) -> str:
    """ Convert text to validate format
    Arguments:
        a {str} -- text to validate
        textlist {list} -- list of valid text
    Returns:
        str -- valid text
    """

    if a is None:
        return None
    for text in textlist:
        if is_similar(a, text):
            return text
    return None

def is_similar(a : str, b : str, threshold : float = 0.5) -> bool:
    """ Check if two strings are similar enough
    
    Arguments:
        a {str} -- first string
        b {str} -- second string
        threshold {float} -- threshold score between 0 and 1
    
    Returns:
        bool -- are similar enough or not
    """
    if a is None or b is None:
        return False
    a = a.lower()
    b = b.lower()
    if a in b or b in a:
        return True
    return SequenceMatcher(a=a, b=b).ratio() > threshold