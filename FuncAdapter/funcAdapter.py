from abc import ABC, abstractmethod, abstractstaticmethod, abstractclassmethod
from pydantic import BaseModel
from typing import Any, Callable, Dict, List, Optional, Type, Union
from types import MethodType, FunctionType
import inspect
import asyncio
from pprint import pprint

def abcmodel(self):
    pass

class Result(list):
    pass

# 适配器抽象基类
class Adapter(ABC):

    @abstractmethod
    def __eventspace__(self) -> Dict[str, Any]:
        '''事件空间'''
        pass

    @abstractmethod
    def match(self) -> bool:
        '''触发器匹配'''
        pass

    @abstractmethod
    def __call__(self) -> Any:
        '''调用方式'''
        pass
    
    @abstractstaticmethod
    def funcevents(*args, **kwargs) -> List[Callable]:
        '''执行器'''
        pass

    @abstractmethod
    def coupler(self) -> Dict:
        '''耦合器'''
        pass

    @abstractmethod
    def callback(self) -> Any:
        '''回调方式'''  
        pass

    _dependent: Dict[type, Any] = {}
    _coupler: Dict[str, Any] = {}
    _funcevents: List[Callable] = []

# 事件函数基类
class AdapterEvent(Adapter, BaseModel):
    
    def match(self) -> bool:
        return True

    def coupler(self) -> dict:
        return self._coupler

    def __eventspace__(self) -> Dict[str, Any]:
        space = {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_back.f_locals)
        self._dependent.update({type(j):j for _,j in space.items()})
        self._dependent.update({type(j):j for _,j in self.dict().items()})
        self._dependent.update({type(j):j for _,j in self._callmethod(self.coupler).items()})
        return space

    def __call__(self, *args, **kwargs) -> Any:
        self.__eventspace__()
        if not self._callmethod(self.match):
            return None
        result = Result()
        for func in self.funcevents():
            result.append(self._callmethod(func))
        self._dependent.update({type(result):result})
        return self._callmethod(self.callback)
    
    def callback(self, result : Result) -> Any:
        pass

    def _injection(self, func: Callable) -> Dict[type, Any]:
        '''依赖注入'''
        f = inspect.signature(func)
        return {j.name:self._dependent[j.annotation] for _,j in f.parameters.items()}

    def _callmethod(self, func: Callable) -> Any:
        '''注释类型方法调用'''
        return func(**self._injection(func))
    
    class Config:
        arbitrary_types_allowed = True

# 异步事件函数基类
class AsyncAdapterEvent(Adapter, BaseModel):
    
    async def match(self) -> bool:
        return True

    async def coupler(self) -> dict:
        return self._coupler

    async def __eventspace__(self) -> Dict[str, Any]:
        space = {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_back.f_locals)
        self._dependent.update({type(j):j for _,j in space.items()})
        self._dependent.update({type(j):j for _,j in self.dict().items()})
        T_coupler =  await self._callmethod(self.coupler)
        self._dependent.update({type(j):j for _,j in T_coupler.items()})
        return space

    async def __call__(self) -> Any:
        print(self.__dict__)
        await self.__eventspace__()
        if not await self._callmethod(self.match):
            return None
        result = Result()
        for func in await self.funcevents():
            result.append(await self._callmethod(func))
        self._dependent.update({type(result):result})
        return await self._callmethod(self.callback)

    async def callback(self, result: Result) -> Any:
        pass

    async def _injection(self, func: Callable) -> Dict[type, Any]:
        f = inspect.signature(func)
        return {j.name:self._dependent[j.annotation] for _,j in f.parameters.items()}
    
    async def _callmethod(self, func: Callable) -> Any:
        return await func(**await self._injection(func))
    
    class Config:
        arbitrary_types_allowed = True

# frame 穿透依赖注入
class FramePenetration:

    def __enter__(self) -> "FramePenetration":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, *args, introduce: Dict[str, Any] = {}):
        space = {}
        self._dependent = {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_locals)
        self._dependent.update({type(j):j for _,j in space.items()})
        self._dependent.update({type(i):i for i in args})
        self._dependent.update({type(j):j for _,j in introduce.items()})

    def __call__(self, *funcs: Callable) -> Any:
        return [self._callmethod(func) for func in funcs]

    def _injection(self, func: Callable) -> Dict[type, Any]:
        '''依赖注入'''
        f = inspect.signature(func)
        return {j.name:self._dependent[j.annotation] for _,j in f.parameters.items()}

    def _callmethod(self, func: Callable) -> Any:
        '''注释类型方法调用'''
        return func(**self._injection(func))

class AsyncFramePenetration:

    async def __aenter__(self) -> "AsyncFramePenetration":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, *args, introduce: Dict[str, Any] = {}):
        space = {}
        self._dependent = {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_locals)
        self._dependent.update({type(j):j for _,j in space.items()})
        self._dependent.update({type(i):i for i in args})
        self._dependent.update({type(j):j for _,j in introduce.items()})

    async def __call__(self, *funcs: Callable, concurrent: bool = False) -> Any:
        if concurrent:
            return [await task for task in [asyncio.create_task(self._callmethod(func)) for func in funcs]]
        return [await self._callmethod(func) for func in funcs]

    async def _injection(self, func: Callable) -> Dict[type, Any]:
        '''依赖注入'''
        f = inspect.signature(func)
        return {j.name:self._dependent[j.annotation] for _,j in f.parameters.items()}

    async def _callmethod(self, func: Callable) -> Any:
        '''注释类型方法调用'''
        return await func(**await self._injection(func))