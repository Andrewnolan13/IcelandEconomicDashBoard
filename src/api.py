'''
Make api class for requesting data
I guess it will be a simple wrapper around requests
But also keep track of number of requests made in the database, don't want to get my IP blocked
I guess make it strictly typed as well
raise for status etc
'''
import requests
import sqlite3
from beartype import beartype # type strict

from .constants import APINode, SOURCE
from .utils import RequestLogger, toTypable
from .exceptions import TooManyRequestsError


class StatisticsIcelandAPI:
    def __init__(self):
        self.__endpoints:dict[str, APINode] = dict()
        self.conn = sqlite3.connect(SOURCE.DATA.DB.str)

    @beartype
    def add_endpoint(self, endpoint: APINode) -> None:
        '''
        Add an endpoint to the API class
        '''
        self.__endpoints[endpoint.englishName] = endpoint
    
    @beartype
    def add_endpoints(self, endpoints: list[APINode]) -> None:
        '''
        Add multiple endpoints to the API class
        '''
        for endpoint in endpoints:
            self.add_endpoint(endpoint)

    @beartype
    def _request(self, endpoint: APINode)->requests.Response:
        '''
        internal use
        raises TooManyRequestsError, RequestException
        
        How it works:
        1. get request the url, this returns metadata about the data cube. You can use this to make a query/slice. Which is just too much work for me here.
        2. format the metadata into a payload that just requests the full thing
        3. post the request with the metadata.
        '''
        # get metadata
        remaining = RequestLogger.queryRemaining(self.conn)
        if remaining <= 0:
            raise TooManyRequestsError("Too many requests made in the last 10 seconds")
        resp = requests.post(endpoint.str,
                             json = {
                                "query": [],
                                "response": {
                                    "format": "csv"
                                }
                            }
                        )
        resp.raise_for_status()

        # # make payload
        # payload = self.build_query_from_metadata(resp.json())
        # # post request
        # resp = requests.post(endpoint.str, json=payload)
        # resp.raise_for_status()
        # # log request
        RequestLogger.log_request(self.conn, endpoint.str, 1.0)
        print("Request made to endpoint: ", endpoint.str,"\nStatus: ",resp.status_code, ".\nRemaining: ", RequestLogger.queryRemaining(self.conn), '\n\n',sep="")
        return resp
    
    @beartype
    def request(self)->dict[str,requests.Response]:
        '''
        request all endpoints and return a dictionary of responses
        raises TooManyRequestsError, RequestException
        '''
        res = dict()
        for endpoint in self.__endpoints.values():
            typable = toTypable(endpoint.englishName)
            res[typable] = self._request(endpoint)
        return res
    
    # @staticmethod
    # def build_query_from_metadata(metadata:dict)->dict:
    #     return {
    #         "query": [
    #             {
    #                 "code": var["code"],
    #                 "selection": {
    #                     "filter": "item",
    #                     "values": var["values"]
    #                 }
    #             } for var in metadata["variables"]
    #         ],
    #         "response": {"format": "csv"}
    #     }