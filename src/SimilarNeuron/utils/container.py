from datetime import datetime, timedelta

class TimeBoundCache():
    '''键值对时限缓存容器'''

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
    
    def updata(self, k, v, timeout : int = None):
        self.put(k)
        self.add(k, v, timeout)
        self._gcCache()

    def put(self, k):
        self._container = [i for i in self._container if i['k']!=k]
        self._gcCache()
    
    def items(self):
        self._gcCache()
        for i in self._container:
            yield i['k'], i['v']

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
    
    def __bool__(self):
        return bool(self._container)

    def _gcCache(self):
        self._container = [i for i in self._container if i['puttime'] > datetime.now()]

class TimeList():
    '''列表时限缓存容器'''

    def __init__(self, timeout : int = 1800):
        self._container = []
        self._timeout = timeout
    
    def add(self, v, timeout : int = None):
        if timeout == None:
            t = self._timeout
        else: 
            t = timeout
        self._container.append({'v': v, 'puttime': datetime.now() + timedelta(seconds=t)})
        self._gcCache()
    
    def updata(self, v, timeout : int = None):
        self.put(v)
        self.add(v, timeout)
        self._gcCache()

    def put(self, v):
        self._container = [i for i in self._container if i['v']!=v]
        self._gcCache()

    def __len__(self):
        self._gcCache()
        return len(self._container)

    def __iter__(self):
        self._gcCache()
        return (i['v'] for i in self._container)

    def __getitem__(self, index):
        self._gcCache()
        if isinstance(index, slice):
            return [i['v'] for i in self._container][index]
    
    def __delitem__(self, index):
        self._gcCache()
        del self._container[index]

    def __contains__(self, v):
        self._gcCache()
        return v in [i['v'] for i in self._container]

    def __bool__(self):
        return bool(self._container)

    def _gcCache(self):
        self._container = [i for i in self._container if i['puttime'] > datetime.now()]

