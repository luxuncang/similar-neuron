from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Callable, Dict, List, Tuple, Union, Any
from ..exception import TransformError

class BaseAgreement(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_agreement(self):
        pass

    @abstractmethod
    def transformation(self):
        pass

class Switch(BaseModel):
    external: Any
    internal: Any
    transform: Callable[[Any], Any]

    def transformation(self, args: Any, judge: bool = False) -> Any:
        if judge: # 严格模式
            res = self.transform(args)
            if isinstance(res, self.internal):
                return res
            raise TransformError()
        return self.transform(args)
    
    def get_agreement(self) -> Tuple[Any, Any]:
        return self.external, self.internal

class Agreement(BaseAgreement):

    def __init__(self, *agreemap: Union[Tuple[Any, Any, Any, Callable], List[Switch]]):
        self.agreemap = agreemap
        