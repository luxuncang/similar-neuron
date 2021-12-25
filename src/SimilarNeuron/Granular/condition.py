from enum import Enum

class State(str, Enum):
    '''状态'''
    success = 'success'
    fail = 'fail'
    cooling = 'cooling'

class Container(list):
    pass