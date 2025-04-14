import sqlite3
import datetime as dt
from .constants import RateLimit, SOURCE

def override(f):
    '''
    Decorator to mark a method as overriding a parent class method.
    Literally does nothing just nice to look at - side effect of learning java I suppose
    '''
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    wrapper.__dict__ = f.__dict__.copy()
    return wrapper

class RequestLogger:
    '''
    simple class to read and write to the REQUESTS table in the database.

    what does it do?
        * Keeps track of the number of requests made per call, with a timestamp, will show url too for debug. 
        * It will also be used to throw an error if there have been too many requests made.
    '''
    @staticmethod
    def queryRemaining(conn:sqlite3.Connection)->float:
        '''
        query the database for the number of requests made in the last ten seconds.
        '''
        cursor = conn.cursor()
        time_10_seconds_ago = (dt.datetime.now() - dt.timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("SELECT SUM(call_weight) FROM REQUESTS WHERE timestamp >= ?", (time_10_seconds_ago,))
        num = cursor.fetchone()[0]
        
        res = RateLimit.TenSecondly.value - num if num is not None else RateLimit.TenSecondly.value
        return float(res) #OCD
    
    @staticmethod
    def log_request(conn:sqlite3.Connection,url:str,call_weight:float)->None:
        '''
        log the request in the database.
        '''
        cursor = conn.cursor()
        cursor.execute("INSERT INTO REQUESTS (url,call_weight) VALUES (?,?)",(url,call_weight))
        conn.commit()
