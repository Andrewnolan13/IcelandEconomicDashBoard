from os.path import dirname, abspath, join
from enum import Enum
from urllib.parse import urljoin
from .utils import override


# Rate limits
class RateLimit(Enum):
    TenSecondly = 10 # ten requests per ten seconds window. ie 10 requests can be made within a 1 - second window but not more than 10 in 10s. Else 429 error


# Safe but conveient path resolution
class PATH:
    '''
    This may be flagged as plagiarism as it is already on github, but I'm the one who wrote it - so technically not I guess
    '''
    parent:'PATH'
    value:str

    def __init__(self,value:str,parent=None,**kwargs):
        if parent is not None:
            if not isinstance(parent, PATH):
                raise TypeError("Parent must be of type PATH")
        if not isinstance(value, str):
            raise TypeError("Value must be a string")
        self.parent = parent
        self.value = value
        for k, v in kwargs.items():
            if not isinstance(v, PATH) and k not in ['parent', 'value']:
                raise TypeError("Value must be of type PATH")
            setattr(self, k, v)
            setattr(v, "parent", self)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return str({K:V for K,V in self.__dict__.items() if K != 'parent'})
    
    @property
    def str(self)->str:
        if self.parent is None:
            return self.value
        return join(self.parent.str, self.value)
    @property
    def leaves(self):
        ls = list()
        for k,v in self.__dict__.items():
            if k not in ['parent', 'value']:
                ls.append(v)
        if len(ls) == 0:
            return [self.str]
        return [leaf for branch in ls for leaf in branch.leaves]
    
    def format(self,**kwargs)->str:
        return self.str.format(**kwargs)

DB = PATH(value = 'database.db')
DATA = PATH(value = 'data',DB = DB)
SOURCE = PATH(value = abspath(join(dirname(__file__),'..')),DATA = DATA)

# urls
endpoint =  'https://px.hagstofa.is/pxen/api/v1/en/'

class URL(PATH):
    @override
    @property
    def str(self)->str:
        if self.parent is None:
            return self.value
        return urljoin(self.parent.str, self.value)
    
INDUSTRIES = URL(value = 'Atvinnuvegir')
ECONOMY = URL(value = 'Efnahagur')
RESIDENTS = URL(value = 'Ibuar')
SOCIETY = URL(value = 'Samfelag')
ENVIRONMENT = URL(value = 'Umhverfi')

ENDPOINT = URL(value = endpoint,
                INDUSTRIES = INDUSTRIES,
                ECONOMY = ECONOMY,
                RESIDENTS = RESIDENTS,
                SOCIETY = SOCIETY,
                ENVIRONMENT = ENVIRONMENT)


