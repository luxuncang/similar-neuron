from abc import ABC

def abcmodel(self):
    ...

def get_abc(classname : str, abcfunc : dict) -> type:
    '''动态创建抽象基类'''
    return type(classname, (ABC,), {i:j(abcmodel) for i,j in abcfunc.items()})

#定义一个元类
class ABCMetaClass(type):
    '''动态创建抽象基类'''

    def __new__(cls, name, bases, attrs):
        print(name)
        if '__abc__' in attrs:
            return type(name, (ABC,), {i:j(abcmodel) for i,j in attrs['__abc__'].items()})


'''
class CLanguage(metaclass=ABCMetaClass):
    __abc__ = {'__init__': abstractmethod}

class Test1(CLanguage):
    
    def __init__(self) -> None:
        super().__init__()

Test1()
'''