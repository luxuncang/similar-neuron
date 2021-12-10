import gc, sys, os, json, asyncio, time
from enum import Enum
from itertools import product, combinations
from typing import Callable, Iterable, Iterator, Dict, Tuple, Union, Any, Set, List, Optional
from abc import ABC, ABCMeta, abstractmethod, abstractstaticmethod
from pydantic import BaseModel
from ..exception import InterfaceTypeError, GranularStateError
from ..utils import dictfilter, TimeBoundCache

mainfile = os.path.split(sys.argv[0])[0]

def structure(cls: "GranularMeta", json: bool = False) -> Dict[Union[str, "GranularMeta"], Iterable]:
    '''实体结构'''

    def method(self) -> Iterator:
        try:
            res = self.__subclasses__()
        except AttributeError:
            return self.iter
        if res:
            return res
        return self

    def _next(clssub: Iterable) -> Union[dict, list]:
        if isinstance(clssub, container):
            return list(clssub)
        return {i: _next(method(i)) for i in clssub}

    def _next_json(clssub: Iterable) -> Union[dict, list]:
        if isinstance(clssub, container):
            return list(clssub)
        return {str(i): _next_json(method(i)) for i in clssub}

    if hasattr(cls, "__subclasses__"):
        subclasses = cls.__subclasses__()
        if not subclasses:
            subclasses = list(cls)
    else:
        subclasses = cls.iter
    if not json:
        return {cls: _next(subclasses)}
    return {str(cls): _next_json(subclasses)}

def iterproduct(cls: "GranularMeta") -> Union[dict, list]:
    granulariter = structure(cls)[cls]
    if len(granulariter) >= 1:
        return granulariter
    return list(cls)

class State(str, Enum):
    '''状态'''
    success = 'success'
    fail = 'fail'
    cooling = 'cooling'

class container(list):
    pass

class GranularMeta(ABCMeta):
    '''实体抽象元类'''

    def __iter__(cls):
        '''终端子域'''
        return (i for i in gc.get_objects() if isinstance(i, cls))
    
    def __hierarchy__(cls) -> Iterator:
        '''层次'''
        d = cls.structure()
        def putk(k: Iterable):
            res = []
            args = []
            for i in k:
                try:
                    res+=list(i.keys())
                    args+=list(i.values())
                except AttributeError:
                    res+=list(i)
            yield res
            if args:
                yield from putk(args)
        yield list(d.keys())
        yield from putk(list(d.values()))        

    def __relationship__(cls, typeset = False) -> Iterator[Union[Set, Tuple]]:
        '''关系'''
        if typeset:
            return list(map(set, product(*(i for i in cls.__subclasses__()))))
        return list(product(*(i for i in cls.__subclasses__())))
    
    def __relationship_map__(cls):
        '''关系映射'''
        return [list(product(*i)) for i in cls.__relationship__()]
    
    def __product__(cls):
        '''笛卡尔积'''
        return list(product(*cls.structure()[cls].keys()))

    def combinations(cls, minimum = 1, typeset: bool = False) -> Iterator[Union[Set, Tuple]]:
        '''所有组合'''
        res = []
        for i in range(minimum, len(cls.next()) + 1):
            res += list(combinations(cls.next(), i))
        if typeset:
            return list(map(set, res))
        return res

    def next(cls):
        '''子域'''
        return list(iterproduct(cls).keys())

    def structure(cls, json: bool = False) -> Dict[Union[str, "GranularMeta"], Iterable]:
        '''实体结构'''
        def method(self) -> Iterator:
            try:
                res = self.__subclasses__()
            except AttributeError:
                return self.iter
            if res:
                return res
            return self

        def _next(clssub: Iterable) -> Union[dict, list]:
            if isinstance(clssub, container):
                return list(clssub)
            return {i: _next(method(i)) for i in clssub}

        def _next_json(clssub: Iterable) -> Union[dict, list]:
            if isinstance(clssub, container):
                return list(clssub)
            return {str(i): _next_json(method(i)) for i in clssub}

        if hasattr(cls, "__subclasses__"):
            subclasses = cls.__subclasses__()
            if not subclasses:
                subclasses = list(cls)
        else:
            subclasses = cls.iter
        if not json:
            return {cls: _next(subclasses)}
        return {str(cls): _next_json(subclasses)}

    def save_structure(cls, path: str = None):
        '''保存实体结构'''
        if not path:
            path = os.path.join(mainfile, "structure.json")
        with open(path, "w", encoding='utf-8') as f:
            f.write(json.dumps(cls.structure(json = True), ensure_ascii=False, indent=4))

class BaseSubstance(metaclass = GranularMeta):
    '''实体抽象基类'''

class Region(BaseSubstance):
    '''域'''

    @abstractmethod
    def add(self):
        ...

    @abstractmethod
    def remote(self):
        ...

    @abstractmethod
    def clear(self):
        ...

    def __iter__(self):
        return iter(self.iter)

class Ordinary(Region):
    '''通用域'''
    
    def __init__(self, name: str, subiter: Iterable[Any] = None) -> None:
        self.name = name
        if subiter:
            self.iter = container(subiter)
        else:
            self.iter = container()

    def add(self, *identification: Iterable[Any]) -> None:
        for i in identification:
            self.iter.append(i)

    def remote(self, *identification: Iterable[Any]) -> None:
        for i in identification:
            self.iter.remove(i)
    
    def clear(self) -> None:
        self.iter.clear()
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name

class BaseRelation(ABC):
    '''关系抽象基类'''

    @abstractmethod
    def success(self) -> bool:
        ...

    @abstractstaticmethod
    def failure() -> bool:
        ...
    
    @abstractmethod
    def cooling(self) -> None:
        ...

class Relation(BaseRelation):
    '''权鉴关系'''

    def __init__(self, frequency: Tuple[int, int] = (1, 0), delayed: int = 0) -> None:
        self.frequency = frequency # n/s 
        self.delayed = delayed

    def cooling(self) -> None:
        ...

    def success(self) -> bool:
        time.sleep(self.delayed)
        return True
    
    @staticmethod
    def failure() -> bool:
        return False

class AsyncRelation(BaseRelation):
    '''权鉴关系'''

    def __init__(self, frequency: Tuple[int, int] = (1, 0), delayed: int = 0) -> None:
        self.frequency = frequency
        self.delayed = delayed

    async def cooling(self) -> None:
        ...

    async def success(self) -> bool:
        await asyncio.sleep(self.delayed)
        return True
    
    @staticmethod
    async def failure() -> bool:
        return False

class Authenticator:
    '''验证器'''

    def __init__(self, state: State, contact: "BaseContext") -> None:
        self.state = state
        self.contact = contact
    
    def run(self):
        if self.state == State.success:
            return self.contact.relationship.success
        elif self.state == State.fail:
            return self.contact.relationship.failure
        elif self.state == State.cooling:
            return self.contact.relationship.cooling
        raise GranularStateError()

class BaseContext(BaseModel):
    '''上下文抽象基类'''
    relationship: BaseRelation = Relation()
    
    @property
    def interfaceType(self) -> Set[Ordinary]:
        return set(
            dictfilter(
                self.dict(),
                filterKey = ['relationship'],
                filterValue = [None]
            )
            .keys()
        )

    @property
    def filterNone(self) -> Dict[Any, Any]:
        return dictfilter(
            self.dict(),
            filterKey = ['relationship'],
            filterValue=[None]
        )

    def rematch(self, contact: "BaseContext") -> bool:
        '''匹配'''
        contactdict:dict = contact.filterNone
        if self.interfaceType != set(contactdict.keys()):
            raise InterfaceTypeError()
        for k,v in contactdict.items():
            if v not in self.dict()[k]:
                return False
        return True

    class Config:
        arbitrary_types_allowed = True

class BaseMapperEvent(Region):
    '''关系映射器基类'''

    def __init__(self, name: str, region: Region, contact: List[BaseContext]):
        self.name = name
        self.region = region
        self.iter: container[BaseContext] = container(contact)
        self.collections = TimeBoundCache(10)
    
    def rematch(self, contact: BaseContext, asyn: bool = False) -> Callable:
        def allmatch(context: BaseContext) -> bool:
            try:
                res =  context.rematch(contact = contact)
                return res
            except InterfaceTypeError:
                return False
        for i in self.iter:
            res = allmatch(i)
            if res:
                k = i.interfaceType
                n = len(self.collections[k])
                if n < i.relationship.frequency[0]:
                    self.collections.add(k, i, i.relationship.frequency[1])
                    return Authenticator(State.success, i).run()
                return Authenticator(State.cooling, i).run()
        if asyn:
            return AsyncRelation.failure
        return Relation.failure

    def add(self, *contact: Iterable[BaseContext]) -> None:
        for i in contact:
            self.iter.append(i)

    def remote(self, *contact: Iterable[BaseContext]) -> None:
        for i in contact:
            self.iter.remove(i)
    
    def clear(self) -> None:
        self.iter.clear()
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
