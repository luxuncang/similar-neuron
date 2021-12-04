from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Callable, Dict, List, Tuple, Union, Any
from ..exception import TransformError, SwitchEmptyError


class BaseAgreement(ABC):

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def get_agreement(self):
        ...

    @abstractmethod
    def transformation(self):
        ...

    @abstractmethod
    def add(self):
        ...

    @abstractmethod
    def remote(self):
        ...

    @abstractmethod
    def clear(self):
        ...



class Switch(BaseModel):
    '''协议转换'''
    external: Any
    internal: Any
    transform: Callable[[Any], Any]

    def transformation(self, args: Any, judge: bool = False) -> Any:
        if judge:  # 严格模式
            res = self.transform(args)
            if isinstance(res, self.internal):
                return res
            raise TransformError()
        return self.transform(args)

    def get_agreement(self) -> Tuple[Any, Any]:
        return self.dict()


class Agreement(BaseAgreement):
    '''协议簇转换'''

    def __init__(self, *agreemap: Switch):
        self.agreemap: Dict[Tuple[Any, Any], Switch] = {
            (i.external, i.internal): i for i in agreemap}

    def transformation(
            self,
            external: Any,
            internal: Any,
            args: Any,
            judge: bool = False) -> Any:
        try:
            return self.agreemap[(external, internal)].transformation(args, judge)
        except KeyError:
            raise SwitchEmptyError()

    def get_agreement(self) -> List[Tuple[Any, Any]]:
        return [i.get_agreement() for i in self.agreemap.values()]

    def add(self, agreemap: Switch):
        self.agreemap.update(
            {(agreemap.external, agreemap.internal): agreemap})

    def remote(self, external: Any, internal: Any):
        self.agreemap.pop((external, internal))

    def clear(self):
        self.agreemap.clear()
