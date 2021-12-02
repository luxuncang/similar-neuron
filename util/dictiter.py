from typing import Iterator

def dictDFS(d: dict) -> Iterator:
    '''python Dict DFS(stop dict.v not dict)'''
    for k,v in d.items():
        if isinstance(v, dict):
            yield (k, v)
            yield from dictDFS(v)
        else:
            yield (k,v)

def dictBSF(d: dict) -> Iterator:
    '''python Dict BSF(stop dict.v not dict)'''
    for k,v in d.items():
        if isinstance(v, dict):
            yield (k,v)
    for k,v in d.items():
        if isinstance(v, dict):
            yield from dictBSF(v)
        else:
            yield (k, v)