import requests
from http import HTTPStatus
import json

from config import ES_HOST, ES_PORT

class ESClientBase:

    def __init__(self, host : str, port : int, index : str, doc_type : str, mapping : dict):
        self._host = host
        self._port = port
        self._es_endpoint = f"{host}:{port}"
        self._index = index
        self._doc_type = doc_type
        self._mapping = mapping

        if self._es_endpoint[:4] != "http":
            if self._port == 443:
                self._es_endpoint = f"https://{self._es_endpoint}" 
            else:
                self._es_endpoint = f"http://{self._es_endpoint}"

    @property
    def index(self):
        return self._index
    
    @property
    def doc_type(self):
        return self._doc_type

    @property
    def mapping(self):
        return self._mapping

    def put_index(self, ignore_exist_error=True) -> requests.Response:
        """ Add an elasticsearch index by sending a put request
        
        Keyword Arguments:
            ignore_exist_error {bool} -- ignore index exist error (default: {True})
        
        Returns:
            requests.Response -- put index http response
        """

        res = requests.put(url=f"{self._es_endpoint}/{self._index}")
        if ignore_exist_error:
            assert res.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST]
        else:
            assert HTTPStatus.OK == res.status_code
        return res
    
    def delete_index(self, ignore_nonexist_error=True) -> requests.Response:
        """ Delete an elasticsearch index by sending a delete request
        
        Keyword Arguments:
            ignore_nonexist_error {bool} -- ignore index not found error (default: {True})
        
        Returns:
            requests.Response -- delete index http response
        """

        res = requests.delete(url=f"{self._es_endpoint}/{self._index}")
        if ignore_nonexist_error:
            assert res.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        else:
            assert HTTPStatus.OK == res.status_code
        return res

    def put_mapping(self) -> requests.Response:
        """ Add an elasticsearch mapping by sending a put request
        
        Returns:
            requests.Response -- put mapping http response
        """

        res = requests.put(url=f"{self._es_endpoint}/{self._index}/_mapping/{self._doc_type}", json=self._mapping)
        assert HTTPStatus.OK == res.status_code
        return res

    def get_document(self, pid : str) -> requests.Response:
        """ Retrieve document by sending a get request
        
        Arguments:
            pid {str} -- primary id
        
        Returns:
            requests.Response -- get document http response
        """

        res = requests.get(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/{pid}")
        return res

    def put_document(self, pid : str, document : dict) -> requests.Response:
        """ Add document by sending a put request
        
        Arguments:
            pid {str} -- primary id
            document {dict} -- document
        
        Returns:
            requests.Response -- put document http response
        """

        res = requests.put(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/{pid}", json=document)
        assert HTTPStatus.CREATED == res.status_code
        return res

    def put_document_bulk(self, pid_list : list, document_list : list) -> requests.Response:
        """ Put multiple documents using batching
        
        Arguments:
            pid_list {list} -- list of primary ids
            document_list {list} -- list of documents
        
        Returns:
            requests.Response -- put request http response
        """

        assert len(pid_list) == len(document_list)
        data_list = [
            "\n".join([
                json.dumps({ "create" : {"_id" : pid, "_type" : self._doc_type, "_index" : self._index} }),
                json.dumps(document)
            ]) for pid, document in zip(pid_list, document_list)
        ]
        data = "\n".join(data_list) + "\n"
        headers = {"Content-Type": "application/x-ndjson"}
        res = requests.post(url=f"{self._es_endpoint}/_bulk?pretty", data=data, headers=headers)
        assert HTTPStatus.OK == res.status_code
        return res

    def delete_document(self, pid : str, ignore_nonexist_error=True) -> requests.Response:
        """ Delete document by sending a delete request
        
        Arguments:
            pid {str} -- Primary id
        
        Keyword Arguments:
            ignore_nonexist_error {bool} -- ignore document not found error (default: {True})
        
        Returns:
            requests.Response -- delete request http response
        """

        res = requests.delete(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/{pid}")
        if ignore_nonexist_error:
            assert res.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        else:
            assert HTTPStatus.OK == res.status_code
        return res

    def delete_document_bulk(self, pid_list : list) -> requests.Response:
        """ Delete multiple documents using batching
        
        Arguments:
            pid_list {list} -- list of primary ids
        
        Returns:
            requests.Response -- post request http response
        """
        # TODO: Need Unittest to Verify If Functionalities are achieved

        data_list = [
            json.dumps({ "delete" : {"_id" : pid, "_type" : self._doc_type, "_index" : self._index} })
            for pid in pid_list
        ]
        data = "\n".join(data_list) + "\n"
        headers = {"Content-Type": "application/x-ndjson"}
        res = requests.post(url=f"{self._es_endpoint}/_bulk?pretty", data=data, headers=headers)
        assert HTTPStatus.OK == res.status_code
        return res

    
    def delete_document_by_query(self, body : dict) -> requests.Response:
        """ Delete queried document
        
        Arguments:
            body {dict} -- query body
        
        Returns:
            requests.Response -- http response
        """

        res = self.search_document(body=body)
        data = res.json()
        if data["hits"]["total"] > 0:
            pid_list = [document["_id"] for document in data["hits"]["hits"]]
            return self.delete_document_bulk(pid_list=pid_list)
        return res

    def search_document(self, body : dict) -> requests.Response:
        """ Search document in elasticsearch
        
        Arguments:
            body {dict} -- query body
        
        Returns:
            requests.Response -- search document http response
        """

        res = requests.get(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/_search", json=body)
        return res
    
    def query_all(self) -> requests.Response:
        """ Select all elements in the index
        
        Returns:
            requests.Response -- search document http response
        """

        query_param = {
            "query" : {
                "match_all" : {}
            }
        }
        res = requests.get(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/_search", json=query_param)
        assert HTTPStatus.OK == res.status_code
        return res

class SBADocument(ESClientBase):

    def __init__(self, host : str = "http://localhost", port : int = 9200, aws_region : str = "us-east-1"):
        
        self.aws_region = aws_region

        index = "sbadocument"
        doc_type = "sbainfo"
        mapping = {
            "properties" : {
                "duns" : {
                    "type" : "integer"
                },
                "company" : {
                    "type" : "text"
                },
                "probability" : {
                    "type" : "float"
                },
                "abstract" : {
                    "type" : "text"
                },
                "award" : {
                    "type" : "float"
                }
            }
        }
        return super().__init__(host, port, index, doc_type, mapping)

    def create_doc_entry(self, duns : int, company : str, probability : float, abstract : str, award : float) -> dict:
        """[summary]
        
        Arguments:
            duns {int} -- [description]
            company {str} -- [description]
            probability {float} -- [description]
            abstract {str} -- [description]
        
        Returns:
            dict -- [description]
        """

        return {
            "duns" : duns,
            "company" : company,
            "probability" : probability,
            "abstract" : abstract,
            "award" : award
        }
    
    def get_company_similar(self, company_name : str) -> dict:
        """ Search document by company name
        
        Arguments:
            company_name {str} -- company name
        
        Returns:
            dict -- dictionary of document
        """

        body = {
            "from": 0,
            "size": 1,
            "query": {
                "bool": {
                    "should": [
                        { "match": { "company": "LLC"}}
                    ]
                }
            }
        }
        
        print(f"search using body: {body}")
        res = self.search_document(body=body).json()
        if len(res["hits"]["hits"]) == 0:
            return {}
        return res["hits"]["hits"][0]["_source"]

    def search_document_by_keywords(self, keywords : list, num_of_docs : int = 100) -> requests.Response:
        """ Search document by keywords

        Arguments:
            keywords {list} -- list of strings to be searched
        
        Keyword Arguments:
            num_of_docs {int} -- max number of searched document (default: {3})
        
        Returns:
            requests.Response -- textfile document contains json() in the form of 
            {
                "..." : ...,
                "hits": {
                    "total": n,
                    "max_scoxre": x.xxxxxxx,
                    "hits": [
                        {
                            "_index" : "...",
                            "_type" : "...",
                            "_id" : "...",
                            "_score" : x.xxxxxxx,
                            "_source" : {...mapping...},
                        },
                    ]
                }
            }
        """

        body = {
            "from" : 0,
            "size" : num_of_docs,
            "query" : {
                "multi_match" : {
                    "query" : " ".join(keywords),
                    "fields" : ["abstract", "company"]
                }
            }
        }

        print(f"search using body: {body}")
        res = self.search_document(body=body)
        return res

if __name__ == "__main__":
    
    sbadoc = SBADocument(host=ES_HOST, port=ES_PORT)
    sbadoc.put_index()
    sbadoc.put_mapping()
    

