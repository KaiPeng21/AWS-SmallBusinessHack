"""
A module that interfaces with Amazon Comprehend Service
"""
import boto3

comprehend = boto3.client("comprehend")
default_language = "en"

def detect_entities(text : str) -> list:
    """ Detect entities in a text
    
    Arguments:
        text {str} -- text to be detected
    
    Returns:
        list -- list of entities in the format of
        [
            {
                'type': 'PERSON'|'LOCATION'|'ORGANIZATION'|'COMMERCIAL_ITEM'|'EVENT'|'DATE'|'QUANTITY'|'TITLE'|'OTHER',
                'content': 'string'
            },
            {
                ...
            },
            ...
        ]
    """
    response = comprehend.detect_entities(
        Text=text,
        LanguageCode=default_language
    )
    return list(map(lambda x : {"type" : x["Type"], "content" : x["Text"]}, response["Entities"]))

def detect_entities_batch(text_list : list) -> list:
    """ Detect entities for texts using batching
    
    Arguments:
        text_list {list} -- list of text to be detected
    
    Returns:
        list -- list of list of entities in the format of
        [
            [
                {
                    'type': 'PERSON'|'LOCATION'|'ORGANIZATION'|'COMMERCIAL_ITEM'|'EVENT'|'DATE'|'QUANTITY'|'TITLE'|'OTHER',
                    'content': 'string'
                },
                {
                    ...
                }
            ],
            [
                ...
            ],
            ...
        ]
    """
    response = comprehend.batch_detect_entities(
        TextList=text_list,
        LanguageCode=default_language
    )
    return list(map(lambda x: list(map(lambda y : {"type" : y["Type"], "content" : y["Text"]}, x["Entities"])), response["ResultList"]))

def detect_keyphrases(text : str) -> list:
    """ Detect key phrases in a text
    
    Arguments:
        text {str} -- text to be detected
    
    Returns:
        list -- list of key phrases in the format of
        [
            'phrase 1',
            'phrase 2',
            ...
        ]
    """
    response = comprehend.detect_key_phrases(
        Text=text,
        LanguageCode=default_language
    )
    return list(map(lambda x : x["Text"], response["KeyPhrases"]))

def detect_keyphrases_batch(text_list : list) -> list:
    """ Detect key phrases in texts using batch
    
    Arguments:
        text_list {list} -- list of text to be detected
    
    Returns:
        list -- list of list of key phrases in the format of
        [
            [
                "phrase 1",
                "phrase 2",
                ...
            ],
            [
                ...
            ],
            ...
        ]
    """
    response = comprehend.batch_detect_key_phrases(
        TextList=text_list,
        LanguageCode=default_language
    )
    return list(map(lambda x: list(map(lambda y: y["Text"], x["KeyPhrases"])), response["ResultList"]))

def detect_sentiment(text : str) -> str:
    """ Detect sentiment in text
    
    Arguments:
        text {str} -- text to be detected
    
    Returns:
        str -- one of 'POSITIVE'|'NEGATIVE'|'NEUTRAL'|'MIXED'
    """

    response = comprehend.detect_sentiment(
        Text=text,
        LanguageCode=default_language
    )
    return response["Sentiment"]

def detect_sentiment_batch(text_list : list) -> list:
    """[summary]
    
    Arguments:
        text_list {list} -- [description]
    
    Returns:
        list -- list of sentiment in the form
        [
            "POSITIVE",
            "NEUTRAL",
            "POSITIVE",
            "NEGATIVE",
            ...
        ]
    """
    response = comprehend.batch_detect_sentiment(
        TextList=text_list,
        LanguageCode=default_language
    )
    return [result["Sentiment"] for result in response["ResultList"]]