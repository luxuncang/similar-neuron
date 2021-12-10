from abc import ABC, abstractmethod, abstractclassmethod
from pydantic import BaseModel
from typing import Callable, Dict, List, Tuple, Union, Any
from ..exception import TransformError, SwitchEmptyError


class BaseAgreement(ABC):
    '''协议簇抽象基类'''

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


class BaseSwitch(ABC):
    '''协议转换抽象基类'''

    external: Any
    internal: Any

    @abstractclassmethod
    def transform(cls, external: Any) -> Any:
        ...

    @classmethod
    def transformation(cls, external: Any, judge: bool = False) -> Any:
        if judge:  # 严格模式
            res = cls.transform(external)
            if isinstance(res, cls.internal):
                return res
            raise TransformError()
        return cls.transform(external)
    
    @classmethod
    def get_agreement(cls) -> Dict[str, Any]:
        return {'external': cls.external, 'internal': cls.internal, 'transform': cls.transform}

class Switch(BaseModel):
    '''协议转换'''
    external: Any
    internal: Any
    transform: Callable[[Any], Any]

    def __init__(__pydantic_self__, external: Any, internal: Any, transform: Callable[[Any], Any]) -> None:
        super().__init__(**{i:j for i,j in locals().items() if i!='__pydantic_self__'})

    def transformation(self, external: Any, judge: bool = False) -> Any:
        if judge:  # 严格模式
            res = self.transform(external)
            if isinstance(res, self.internal):
                return res
            raise TransformError()
        return self.transform(external)

    def get_agreement(self) -> Dict[str, Any]:
        return self.dict()


class Agreement(BaseAgreement):
    '''协议簇转换'''

    def __init__(self, *agreemap: Union[Switch, BaseSwitch]):
        self.agreemap: Dict[Tuple[Any, Any], Union[Switch, BaseSwitch]] = {
            (i.external, i.internal): i for i in agreemap}

    def transformation(
            self,
            external: Any,
            internal: Any,
            judge: bool = False) -> Any:
        try:
            return self.agreemap[(type(external), internal)].transformation(external, judge)
        except KeyError:
            raise SwitchEmptyError()

    def get_agreement(self) -> List[Dict[Any, Any]]:
        return [i.get_agreement() for i in self.agreemap.values()]

    def add(self, agreemap: Union[Switch, BaseSwitch]):
        self.agreemap.update(
            {(agreemap.external, agreemap.internal): agreemap})

    def remote(self, external: Any, internal: Any):
        self.agreemap.pop((external, internal))

    def clear(self):
        self.agreemap.clear()