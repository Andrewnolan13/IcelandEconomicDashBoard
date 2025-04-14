def override(f):
    '''
    Decorator to mark a method as overriding a parent class method.
    Literally does nothing just nice to look at - side effect of learning java I suppose
    '''
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    wrapper.__dict__ = f.__dict__.copy()
    return wrapper    
