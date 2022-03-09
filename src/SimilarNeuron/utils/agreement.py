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
            if isinstance(cls.internal, str) and type(res).__name__ == cls.internal:
                return res
            elif (not isinstance(cls.internal, str)) and isinstance(res, cls.internal):
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
            if isinstance(self.internal, str) and type(res).__name__ == self.internal:
                return res
            elif (not isinstance(self.internal, str)) and isinstance(res, self.internal):
                return res
            raise TransformError()
        return self.transform(external)

    def get_agreement(self) -> Dict[str, Any]:
        return self.dict()
    
    def __hash__(self):
        return hash((self.external, self.internal, self.transform))


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

        return self.find_agreement(external, internal).transformation(external, judge)

    def get_agreement(self) -> List[Dict[Any, Any]]:
        return [{'switch': i , **i.get_agreement()} for i in self.agreemap.values()]

    def find_agreement(self, external: Any, internal: Any) -> Union[Switch, BaseSwitch]: # 可以改进

        type_external = type(external)
        res = self.agreemap.get((type(external), internal)) # 已存在
        if res:
            return res
        agreements = self.get_agreement()
        temp_a = [i['switch'] for i in agreements if i['external'] == type_external]
        temp_b = [i['switch'] for i in agreements if (not isinstance(i['external'], str)) and i['external'].__name__ == type_external.__name__]
        temp_c = [i['switch'] for i in agreements if isinstance(i['external'], str) and i['external'] == type_external.__name__]
        ex_temp = temp_a + temp_b + temp_c
        print(ex_temp)
        ex_temp = set(ex_temp)
        temp_a = set([i['switch'] for i in agreements if i['internal'] == internal])
        temp_b = set([i['switch'] for i in agreements if (not isinstance(i['internal'], str)) and i['internal'].__name__ == internal])
        temp_c = set([i['switch'] for i in agreements if isinstance(i['internal'], str) and (not isinstance(internal, str)) and i['internal'] == internal.__name__])
        in_temp = temp_a | temp_b | temp_c
        temp = ex_temp & in_temp
        if temp:
            return temp.pop()
        raise SwitchEmptyError()

    def add(self, agreemap: Union[Switch, BaseSwitch]):
        self.agreemap.update(
            {(agreemap.external, agreemap.internal): agreemap})

    def remote(self, external: Any, internal: Any):
        self.agreemap.pop((external, internal))

    def clear(self):
        self.agreemap.clear()