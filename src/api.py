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
from .utils import RequestLogger
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
        '''
        remaining = RequestLogger.queryRemaining(self.conn)
        if remaining <= 0:
            raise TooManyRequestsError("Too many requests made in the last 10 seconds")
        resp = requests.get(endpoint.str)
        RequestLogger.log_request(self.conn, endpoint.str, 1.0)
        resp.raise_for_status()
        return resp
    
    @beartype
    def request(self)->dict[str,requests.Response]:
        '''
        request all endpoints and return a dictionary of responses
        raises TooManyRequestsError, RequestException
        '''
        res = dict()
        for endpoint in self.__endpoints.values():
            res[endpoint.englishName] = self._request(endpoint)
        return res