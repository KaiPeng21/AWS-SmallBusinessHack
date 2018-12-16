"""
This script ingest the sagemaker output from dummy.json to elasticsearch
"""

import json
from config import ES_HOST, ES_PORT
from client_comprehend import detect_keyphrases, detect_keyphrases_batch
from esclient import SBADocument

sbadoc = SBADocument(host=ES_HOST, port=ES_PORT)

# Need provide dummy.json and run this script from the src directory
with open("dummy-output.json", "r") as file:
  data = json.loads(file.read())

pid_list = [entry["company"] for entry in data]

sbadoc.put_document_bulk(pid_list=pid_list, document_list=data)