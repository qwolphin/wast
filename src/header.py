from __future__ import annotations
import ast
import attrs
from typing import Optional, Sequence, Callable
from .validators import (
    convert_identifier,
    DeepIterableConverter,
    ProxyInstanceOfValidator,
)


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
    def __getattr__(self, name):
        return BoundUnderscore(Name(id=name))

    def __call__(self, name, *attrs):
        ret = Name(id=name)
        for name in reversed(attrs):
            ret = Attribute(value=ret, attr=name)

        return BoundUnderscore(ret)


_ = FreeUnderscore()


class BoundUnderscore(object):
    def __repr__(self):
        return f"BoundUnderscore({self.__inner__})"

    def __init__(self, inner):
        assert isinstance(inner, expr)
        self.__inner__ = inner

    def __getattr__(self, name):
        return BoundUnderscore(Attribute(value=self.__inner__, attr=name))

    def __call__(self, *args, **kwargs):
        return BoundUnderscore(
            Call(
                func=self.__inner__,
                args=args,
                keywords=[keyword(value=v, arg=k) for k, v in kwargs.items()],
            )
        )

    def __add__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Add(), right=other.__inner__)
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = slice(lower=key.start, upper=key.stop, step=key.step)

        return BoundUnderscore(Subscript(slice=key, value=self.__inner__))

    @property
    def _(self):
        return self.__inner__
