from os.path import dirname, abspath, join
from enum import Enum

__all__ = ['RateLimit', 'PATH', 'SOURCE', 'APINode', 'ENDPOINTS']

# Rate limits
class RateLimit(Enum):
    '''
    Overkill but makes code readable
    '''
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
ASSETS = PATH(value = 'assets',ENDPOINT_TREE = PATH('endpointTree.json'))
SOURCE = PATH(value = abspath(join(dirname(__file__),'..')),DATA = DATA,ASSETS = ASSETS)

# urls
import re
import json

pattern = re.compile(r"\d+\-\d+")

def toTypable(s:str) -> str:
    """Convert a string to a typable format by removing special characters and replacing spaces with underscores."""
    s = re.sub(r"[^a-zA-Z0-9_\-]", "_", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(pattern, lambda m: m.group(0).replace("-", "_to_"), s)
    return s

class APINode:
    '''
    similar idea to PATH but read from json
    makes code readable
    prevents typos
    all dat
    '''
    BASE_URL = "https://px.hagstofa.is/pxen/api/v1/en"
    def __init__(self, pathComponent:str,parent:'APINode', children:dict=dict()):
        self.__pathComponent = pathComponent
        self.__children = children.copy() #shallow good
        self.__englishName = self.__children.pop('englishName', 'baseURL') 
        self.__parent = parent # can be None
        self.isLeaf = False # if it's a leaf, then it's a table

        self.__recurse()

    def __recurse(self):
        '''
        give it attributes by running through the children dict recusrively.
        eg the url https://px.hagstofa.is/pxen/api/v1/en/Atvinnuvegir/ferdathjonusta/ferdaidnadurhagvisar
        should be retrieved by obj.Atvinnuvegir.Tourism.Short_term_indicators_in_tourism
        so englishName has a purpose.
        obviously the latter is so much more readable than the former.
        also user friendly
        '''        
        if self.__children.get('leaf'):
            self.isLeaf = True
            return
        for pathComponent, children in self.__children.items():
            tmp = APINode(pathComponent=pathComponent, parent=self, children=children)
            typableEnglishName = toTypable(tmp.__englishName)
            setattr(self, typableEnglishName, tmp)
    
    @property
    def englishName(self)->str:
        return str(self.__englishName)
    
    @property
    def str(self)->str:
        if self.__parent:
            return f"{self.__parent.str}/{self.__pathComponent}"
        else:
            return self.__pathComponent

    def __str__(self):
        return self.str

    def __repr__(self):
        return f"<APINode {self}>"
    

with open(SOURCE.ASSETS.ENDPOINT_TREE.str, 'r') as f:
    tree = json.load(f)
    ENDPOINTS = APINode(pathComponent=APINode.BASE_URL, parent=None, children=tree)

