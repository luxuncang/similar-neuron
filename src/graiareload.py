from typing import Callable
from watchgod import arun_process
from asyncio import AbstractEventLoop
from graia.application import GraiaMiraiApplication
import os

async def watchfile(reload: Callable[[], None]) -> None:
    await arun_process(os.getcwd(), reload)

def main(loop: AbstractEventLoop, reload: Callable[[], None]) -> None:
    loop.create_task(watchfile(reload))
    loop.run_forever()

class GraiaStarter():

    def __init__(self, loop: AbstractEventLoop, app: GraiaMiraiApplication, reload: Callable) -> None:
        self.loop = loop
        self.app = app
        self.reload = reload
    
    async def watchfile(self) -> None:
        await arun_process(os.getcwd(), self.reload)
    
    def run(self, reload: bool = False) -> None:
        if reload:
            self.loop.create_task(self.watchfile())
            self.loop.run_forever()
        else:
            self.app.launch_blocking()
