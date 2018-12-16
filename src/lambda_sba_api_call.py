"""
SBA API Porting Lambda Handler
"""

import boto3
import os
import json
from http import HTTPStatus

from esclient import SBADocument
from client_comprehend import detect_keyphrases
from config import ES_HOST, ES_PORT

sbadoc = SBADocument(host=ES_HOST, port=ES_PORT)

def lambda_handler(event, context):
    print(f"handling lambda using event: {event}")

    resource = event["resource"]

    if resource == "/":
        return index(event, context)

    if resource.startswith("/company/"):
        return company(event, context)

    if resource.startswith("/abstract/"):
        return abstract(event, context)

    return create_response("bad request", status_code=HTTPStatus.BAD_REQUEST)


def index(event, context):

    body = {
        "data" : "Welcome to Small Business Hackathon!"
    }

    return create_response(body)

def company(event, context):

    path_params, query_params = retrieve_params(event)

    company_name = path_params["companyName"]

    resp = sbadoc.get_document(pid=company_name).json()

    if not resp["found"]:
        return not_found()

    body = resp["_source"]

    return create_response(body)

def abstract(event, context):

    path_params, query_params = retrieve_params(event)

    num_of_docs = 100
    if "n" in query_params.keys():
        num_of_docs = query_params["n"]

    descrioption = path_params["description"]
    keywords = detect_keyphrases(descrioption)
    if len(keywords) > 0:
        resp = sbadoc.search_document_by_keywords(keywords, num_of_docs=num_of_docs).json()
    else:
        resp = sbadoc.search_document_by_keywords(descrioption.split(), num_of_docs=num_of_docs).json()
    
    hit_list = sorted(resp["hits"]["hits"], key=lambda x: (-x["_score"], -x["_source"]["probability"]))
    
    body = [{**hit["_source"], "searchRelevance" : hit["_score"]} for hit in hit_list]
    #body = sorted([hit["_source"] for hit in resp["hits"]["hits"]], key=lambda x: -x["probability"])

    return create_response(body)

def not_found():
    return {
        "statusCode" : HTTPStatus.NOT_FOUND,
        "body" : "404 resource not found"
    }

def create_response(body, status_code = HTTPStatus.OK) -> dict:
    return {
        "statusCode" : status_code,
        "headers": {
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : True
        },
        "body" : json.dumps(body) if isinstance(body, (list, dict)) else body
    }

def retrieve_params(event) -> tuple:
    path_params = event.get("pathParameters") if event.get("pathParameters") is not None else {}
    query_params = event.get("queryStringParameters") if event.get("queryStringParameters") is not None else {}
    return path_params, query_params