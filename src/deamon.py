import pandas as pd
import sqlite3
import multiprocessing
import time
import requests
from io import StringIO

from .constants import APINode, ENDPOINTS, SOURCE
from .api import StatisticsIcelandAPI

class DataRefresher(multiprocessing.Process):
    '''
    This will run in the background as a separate process
    on init it will accept an endpoint to request data from
    it will also accept a table name and sleep period

    wait - wait this long before starting the process -  this is so if I make 100 deamon proceses, I can stagger them

    from there it will periodically request data from the endpoint, clean the data and write it to the database 
    '''
    def __init__(self, endpoint:APINode, table_name:str, sleep_period:int, wait:int, alive_event:multiprocessing.Event): # type: ignore
        super().__init__()
        self.endpoint = endpoint
        self.table_name = table_name
        self.sleep_period = sleep_period
        self.alive_event = alive_event
        self.wait = wait

    def run(self):
        '''
        run the process
        '''
        time.sleep(self.wait)
        # make api object
        api = StatisticsIcelandAPI()
        api.add_endpoint(self.endpoint)

        # loop
        while self.alive_event.is_set():
            try:
                response = api._request(self.endpoint)
                df = self.processResponse(response)
                df.to_sql(
                    self.table_name,
                    con=api.conn,
                    if_exists='replace',
                    index=False,
                )

                print(f"Refreshed {self.table_name} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(self.sleep_period)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                with open(SOURCE.ASSETS.LOG.str+f'_{multiprocessing.current_process().name}.txt', 'a') as f:
                    f.write(f"Error refreshing {self.table_name} at {time.strftime('%Y-%m-%d %H:%M:%S')}: {e}\n")
                    time.sleep(self.sleep_period)                            


    @staticmethod
    def processResponse(response:requests.Response)->pd.DataFrame:
        '''
        Do Data processing here.
        This prevents it being done by the callbacks.
        '''
        df = DataRefresher.__convert_to_df(response)
        df.replace(r'^\.+$','0', regex=True) # for some reason nan values arrive as . or ..
        df = df.convert_dtypes()

        return df 
        
    

    @staticmethod
    def __convert_to_df(response:requests.Response)->pd.DataFrame:
        '''
        convert response text into a pandas DataFrame
        '''
        return pd.read_csv(
            StringIO(response.text.lstrip('ï»¿')),
            sep=',',
            encoding='utf-8'
        )              






