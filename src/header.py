from __future__ import annotations
import ast
import attr as attrs
from typing import Optional, Sequence, Callable
from .validators import convert_identifier, DeepIterableConverter, ProxyInstanceOfValidator

def unparse(node):
    n = ast.fix_missing_locations(node._to_builtin())
    return ast.unparse(n)

def parse(text):
    node = ast.parse(text)
    return node_to_wast(node)

class Node:
    pass

def node_to_wast(node):
    match node:
        case int() | float() | str() | None:
            return node
        case list() | tuple():
            return [node_to_wast(x) for x in node]
        case _:
            return globals()[node.__class__.__name__]._from_builtin(node)


def wast_to_node(node):
    match node:
        case int() | float() | str() | None:
            return node
        case list() | tuple():
            return [wast_to_node(x) for x in node]
        case _:
            return node._to_builtin()

class FreeUnderscore:
    def __getattribute__(self, name):
        return w.Name(id=name)

_ = FreeUnderscore()

class BoundUnderscore(object):
    F89tRaS7LrnWJyur8gPTI7: list # inner FIXME

    def __init__(self, inner_node):
        self.F89tRaS7LrnWJyur8gPTI7 = inner_node

    def __getattr__(self, name):
        n = self.F89tRaS7LrnWJyur8gPTI7
        return Attribute(value=self.F89tRaS7LrnWJyur8gPTI7, attr=name)

    def __call__(self, *args, **kwargs):
        n = self.F89tRaS7LrnWJyur8gPTI7
        return Call(func=n, args=args, keywords=[keyword(value=v, arg=k) for k, v in kwargs.items()])

    def __getitem__(self, key):
        n = self.F89tRaS7LrnWJyur8gPTI7
        if isinstance(key, slice):
            key = w.slice(lower=key.start, upper=key.stop, step=key.step)

        return w.Subscript(slice=key, value=n)
