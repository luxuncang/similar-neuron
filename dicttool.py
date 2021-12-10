from typing import Any, Iterable, Iterator, Hashable

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

def dictfilter(d: dict, *, filterKey: Iterable[Hashable] = [], filterValue: Iterable[Any] = []) -> dict:
    '''python Dict filter(According to the dictionary key name or value)'''
    return {k:v for k,v in d.items() if (k not in filterKey) and (v not in filterValue)}