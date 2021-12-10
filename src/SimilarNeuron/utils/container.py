from datetime import datetime, timedelta
import time

from pydantic.fields import T

class TimeBoundCache():
    '''时限缓存容器'''

    def __init__(self, timeout : int = 1800):
        self._container = []
        self._timeout = timeout
    
    def add(self, k, v, timeout : int = None):
        if timeout == None:
            t = self._timeout
        else: 
            t = timeout
        self._container.append({'k': k, 'v': v, 'puttime': datetime.now() + timedelta(seconds=t)})
        self._gcCache()
    
    def put(self, k):
        self._container = [i for i in self._container if i['k']!=k]
        self._gcCache()
    
    def __len__(self):
        self._gcCache()
        return len(self._container)

    def __iter__(self):
        self._gcCache()
        return ({i['k']:i['v']} for i in self._container)

    def __getitem__(self, index):
        self._gcCache()
        if isinstance(index, slice):
            return [{i['k']:i['v']} for i in self._container][index]
        else:
            return [i['v'] for i in self._container if i['k']==index]
    
    def __delitem__(self, index):
        self._gcCache()
        self._container = [i for i in self._container if i['k']!=index]

    def __contains__(self, k):
        self._gcCache()
        return k in [i['k'] for i in self._container]

    def _gcCache(self):
        self._container = [i for i in self._container if i['puttime'] > datetime.now()]

