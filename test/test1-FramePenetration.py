from FuncAdapter import FramePenetration, AsyncFramePenetration
import asyncio

class Event_A():
    def __repr__(self):
        return 'Event_A'

class Event_B():
    def __repr__(self):
        return 'Event_B'

class Event_C():
    def __repr__(self):
        return 'Event_C'

def main_1(a: Event_A, b: Event_B, c: Event_C):
    print(a, b, c)
    return a,b,c

def main_2(b: Event_B, c: Event_C):
    print(b, c)
    return b,c

async def main_3(a: Event_A, b: Event_B, c: Event_C):
    print(a, b, c)
    return a,b,c

async def main_4(b: Event_B, c: Event_C):
    print(b, c)
    return b,c

e3: Event_C = Event_C()

def receiver(e1: Event_A, e2: Event_B):
    with FramePenetration(introduce={'e3':e3}) as runfunc:
        print(runfunc(main_1, main_2))

async def receiver_async(e1: Event_A, e2: Event_B):
    async with AsyncFramePenetration(e3) as runfunc:
        print(await runfunc(main_3, main_4, concurrent = True))


receiver(Event_A(), Event_B())
asyncio.run(receiver_async(Event_A(), Event_B()))
# await receiver_async(Event_A(), Event_B()) # In jupyter