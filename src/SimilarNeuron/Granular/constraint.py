from SimilarNeuron.FuncAdapter.funcAdapter import Result
from pydantic import BaseModel
from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Callable, Iterable, Iterator, Dict, Tuple, Union, Any, Set, List, Optional
import asyncio, time

from ..exception import InterfaceTypeError, GranularStateError
from ..utils import dictfilter, TimeBoundCache
from .condition import State, Container
from .granular import Ordinary, Region, Ordinary


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
    direction: bool = True
    
    @property
    def interfaceType(self) -> Set[Ordinary]:
        return set(
            dictfilter(
                self.dict(),
                filterKey = ['relationship', 'direction', 'name'],
                filterValue = [None]
            )
            .keys()
        )

    @property
    def filterNone(self) -> Dict[Any, Any]:
        return dictfilter(
            self.dict(),
            filterKey = ['relationship', 'direction', 'name'],
            filterValue=[None]
        )

    def rematch(self, contact: "BaseContext") -> bool:
        '''匹配'''
        contactdict:dict = contact.filterNone
        if self.interfaceType != set(contactdict.keys()):
            raise InterfaceTypeError()
        return next(
            (
                self.direction == False
                for k, v in contactdict.items()
                if v not in self.dict()[k]
            ),
            self.direction == True,
        )

    def location(self, contact: "BaseContext") -> Union[bool, "BaseContext"]:
        '''定位'''
        contactdict:dict = contact.filterNone
        for k,v in contactdict.items():
            if k not in self.filterNone:
                raise InterfaceTypeError()
        for k,v in contactdict.items():
            if v not in self.dict()[k]:
                raise InterfaceTypeError()
        return self

    class Config:
        arbitrary_types_allowed = True

class BaseMapperEvent(Ordinary):
    '''关系映射器基类'''

    def __init__(self, name: str, region: Ordinary, contact: List[BaseContext]):
        self.name = name
        self.region = region
        self.iter: Container[BaseContext] = Container(contact)
        self.collections = TimeBoundCache(10)
    
    def rematch(self, contact: BaseContext, asyn: bool = False) -> Callable:
        def allmatch(context: BaseContext) -> bool:
            try:
                return context.rematch(contact = contact)
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
    
    def match(self, contact: BaseContext) -> bool:
        def allmatch(context: BaseContext) -> bool:
            try:
                return context.rematch(contact = contact)
            except InterfaceTypeError:
                return False
        for i in self.iter:
            res = allmatch(i)
            if res:
                return res
        return False
    
    def location(self, contact: BaseContext) -> Union[bool, BaseContext]:
        result = []
        def allmatch(context: BaseContext) -> bool:
            try:
                return context.location(contact = contact)
            except InterfaceTypeError:
                ...
        for i in self.iter:
            res = allmatch(i)
            if res:
                result.append(res)
        return result

