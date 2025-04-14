
class UserException(Exception):
    '''
    Base class for all exceptions related to user input or actions.
    Exceptions intentionally raised so that the user does not get banned or has done something wrong or something.
    '''
    pass

class TooManyRequestsError(UserException):
    """Exception raised when too many requests are made to the API."""
    pass