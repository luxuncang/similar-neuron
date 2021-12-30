from abc import ABC, abstractmethod, abstractstaticmethod
from pydantic import BaseModel
from typing import Any, Callable, Dict, List
import inspect
import asyncio

from ..exception import AnnotationEmpty

class Result(list):
    '''Adapter evnet result'''
    
    def first(self):
        '''Return first result'''
        return self[0]

class EventName(str):
    '''Adapter class name'''
    ...

# 适配器抽象基类
class Adapter(ABC):

    @abstractmethod
    def __eventspace__(self) -> Dict[str, Any]:
        '''事件空间'''
        ...

    @abstractmethod
    def match(self) -> bool:
        '''触发器匹配'''
        ...

    @abstractmethod
    def __call__(self) -> Any:
        '''调用方式'''
        ...
    
    @abstractstaticmethod
    def funcevents(*args, **kwargs) -> List[Callable]:
        '''执行器'''
        ...

    @abstractmethod
    def coupler(self) -> Dict:
        '''耦合器'''
        ...

    @abstractmethod
    def callback(self) -> Any:
        '''回调方式'''  
        ...

    @staticmethod
    def paramdefault(default) -> Any:
        '''默认参数'''
        if default == inspect.Parameter.empty:
            return None
        return default

class Frame(ABC):
    '''Frame'''

    @staticmethod
    def paramdefault(default) -> Any:
        '''默认参数'''
        if default == inspect.Parameter.empty:
            return None
        return default

# 事件函数基类
class AdapterEvent(Adapter, BaseModel):

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def run(self) -> Any:
        '''运行方法'''
        self.__eventspace__()
        if not self._callmethod(self.match):
            return None
        result = Result()
        for func in self._callmethod(self.funcevents):
            result.append(self._callmethod(func))
        self._dependent.update({type(result):result})
        return self._callmethod(self.callback)

    def match(self) -> bool:
        return True

    def coupler(self) -> dict:
        return {}

    def __eventspace__(self) -> Dict[str, Any]:
        space,self._dependent = {}, {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_back.f_locals)
        self._dependent.update({EventName: self.__class__.__name__})
        self._dependent.update(
            {type(j): j for _, j in space.items()}
        )
        self._dependent.update(
            {type(j): j for _, j in self.dict().items()}
        )
        self._dependent.update(
            {type(i): i for i in self._callmethod(
                self.coupler
                )
            }
        )
        return space

    def __call__(self, *args, **kwargs) -> Any:
        self.__eventspace__()
        if not self._callmethod(self.match):
            return None
        result = Result()
        for func in self._callmethod(self.funcevents()):
            result.append(self._callmethod(func))
        self._dependent.update({type(result):result})
        return self._callmethod(self.callback)
    
    def callback(self, result : Result) -> Any:
        pass

    def _injection(self, func: Callable) -> Dict[type, Any]:
        '''依赖注入'''
        res = {}
        f = inspect.signature(func)
        for name, param in f.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                res[name] = self._dependent.get(param.annotation) if not self._dependent.get(param.annotation) is None else self.paramdefault(param.default)
            else:
                raise AnnotationEmpty(reason = f'{name} annotation is empty!')
        return res

    def _callmethod(self, func: Callable) -> Any:
        '''注释类型方法调用'''
        return func(**self._injection(func))
    
    def eventspace(self) -> Dict[str, Any]:
        '''事件空间'''
        return self._dependent

    def callfunc(self, func: Callable) -> Any:
        '''调用函数(无感知依赖注入)'''
        return self._callmethod(func)

    def addeventspace(self, *introduce) -> None:
        '''添加事件空间'''
        self._dependent.update({type(i): i for i in introduce})

    def removeeventspace(self, *remove) -> None:
        '''移除事件空间'''
        for i in remove:
            self._dependent.pop(type(i))

    class Config:
        arbitrary_types_allowed = True

# 异步事件函数基类
class AsyncAdapterEvent(Adapter, BaseModel):
    
    def __setattr__(self, key, value):
        self.__dict__[key] = value

    async def run(self) -> Any:
        self._dependent = {}
        await self.__eventspace__()
        if not await self._callmethod(self.match):
            return None
        result = Result()
        for func in await self._callmethod(self.funcevents):
            result.append(await self._callmethod(func))
        self._dependent.update({type(result):result})
        return await self._callmethod(self.callback)

    async def match(self) -> bool:
        return True

    async def coupler(self) -> dict:
        return {}

    async def __eventspace__(self) -> Dict[str, Any]:
        space,self._dependent = {}, {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_back.f_locals)
        self._dependent.update({EventName: self.__class__.__name__})
        self._dependent.update(
            {type(j):j for _,j in space.items()}
            )
        self._dependent.update(
            {type(j):j for i,j in self.dict().items() if i != '_dependent'}
            )
        T_coupler =  await self._callmethod(self.coupler)
        self._dependent.update(
            {type(i):i for i in T_coupler}
            )
        return space

    async def __call__(self) -> Any:
        self._dependent = {}
        await self.__eventspace__()
        if not await self._callmethod(self.match):
            return None
        result = Result()
        for func in await self._callmethod(self.funcevents):
            result.append(await self._callmethod(func))
        self._dependent.update({type(result):result})
        return await self._callmethod(self.callback)

    async def callback(self, result: Result) -> Any:
        pass

    async def _injection(self, func: Callable) -> Dict[type, Any]:
        '''依赖注入'''
        res = {}
        f = inspect.signature(func)
        for name, param in f.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                res[name] = self._dependent.get(param.annotation) if not self._dependent.get(param.annotation) is None else self.paramdefault(param.default)
            else:
                raise AnnotationEmpty(reason = f'{name} annotation is empty!')
        return res

    async def _callmethod(self, func: Callable) -> Any:
        return await func(**await self._injection(func))
    
    async def eventspace(self) -> Dict[str, Any]:
        '''事件空间'''
        return self._dependent

    async def callfunc(self, func: Callable) -> Any:
        '''调用函数(无感知依赖注入)'''
        return await self._callmethod(func)

    async def addeventspace(self, *introduce) -> None:
        '''添加事件空间'''
        self._dependent.update({type(i): i for i in introduce})

    async def removeeventspace(self, *remove) -> None:
        '''移除事件空间'''
        for i in remove:
            self._dependent.pop(type(i))

    class Config:
        arbitrary_types_allowed = True

# frame 穿透依赖注入
class FramePenetration(Frame):

    def __enter__(self) -> "FramePenetration":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, *args, introduce: Dict[str, Any] = None):
        space, self._dependent= {}, {}
        if not introduce:
            introduce = {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_locals)
        self._dependent.update(
            {type(j):j for _,j in space.items()}
            )
        self._dependent.update(
            {type(i):i for i in args}
            )
        self._dependent.update(
            {type(j):j for _,j in introduce.items()}
            )

    def __call__(self, *funcs: Callable) -> Any:
        return [self._callmethod(func) for func in funcs]

    def _injection(self, func: Callable) -> Dict[type, Any]:
        '''依赖注入'''
        res = {}
        f = inspect.signature(func)
        for name, param in f.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                res[name] = self._dependent.get(param.annotation) if not self._dependent.get(param.annotation) is None else self.paramdefault(param.default)
            else:
                raise AnnotationEmpty(reason = f'{name} annotation is empty!')
        return res

    def _callmethod(self, func: Callable) -> Any:
        '''注释类型方法调用'''
        return func(**self._injection(func))

class AsyncFramePenetration(Frame):

    async def __aenter__(self) -> "AsyncFramePenetration":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, *args, introduce: Dict[str, Any] = None):
        space, self._dependent= {}, {}
        if not introduce:
            introduce = {}
        frame = inspect.currentframe()
        space.update(frame.f_back.f_locals)
        self._dependent.update(
            {type(j):j for _,j in space.items()}
            )
        self._dependent.update(
            {type(i):i for i in args}
            )
        self._dependent.update(
            {type(j):j for _,j in introduce.items()}
            )

    async def __call__(self, *funcs: Callable, concurrent: bool = False) -> Any:
        if concurrent:
            return [await task for task in [asyncio.create_task(self._callmethod(func)) for func in funcs]]
        return [await self._callmethod(func) for func in funcs]

    async def _injection(self, func: Callable) -> Dict[type, Any]:
        '''依赖注入'''
        res = {}
        f = inspect.signature(func)
        for name, param in f.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                res[name] = self._dependent.get(param.annotation) if not self._dependent.get(param.annotation) is None else self.paramdefault(param.default)
            else:
                raise AnnotationEmpty(reason = f'{name} annotation is empty!')
        return res

    async def _callmethod(self, func: Callable) -> Any:
        '''注释类型方法调用'''
        return await func(**await self._injection(func))
    
