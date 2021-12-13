'''AdapterEvent example'''

from SimilarNeuron import AdapterEvent, Result
from typing import Any, List, Callable, Dict, Iterable

# 公用依赖
class AppMode:
    name : str = "AppMode"
    version : str = "0.0.1"

# 外部依赖
class MessageChain:
    def __init__(self, message: Dict[str, Any]):
        self.message = message

# 自定义类型
class Text():
    def __init__(self, text: Iterable):
        self.text = text
    
    def get_text(self):
        return ' '.join(self.text)

class TestEvnet(AdapterEvent):
    '''测试事件'''
    appmodel: AppMode = AppMode() # 注入事件通用依赖

    @staticmethod
    def funcevents() -> List[Callable]:
        '''事件簇'''
        def on_start(app: AppMode):
            print('on_start', app.name, app.version)
            return True
        def on_stop(text: Text):
            print('on_stop', text.get_text())
            return True
        def on_pause():
            print('on_pause')
            return True
        return [on_start, on_stop, on_pause]
    
    def coupler(self, message: MessageChain) -> dict:
        '''协议转换'''
        
        return {
            'text': Text(message.message.keys())
        }
    
    def match(self) -> bool:
        '''匹配事件'''
        return True
    
    def callback(self, result: Result, app: AppMode) -> bool:
        '''回调函数'''
        print(f'result: {result}', app, sep = '\n')


def main(message):
    '''主函数'''
    TestEvnet().run() # 实例化该事件

# 循环主函数
for i in map(main, [MessageChain({'m-001': 1, 'm-002': 2}), MessageChain({'m-003': 3, 'm-004': 4})]):
    print(i)