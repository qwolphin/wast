from __future__ import annotations
import ast
import attrs
from typing import Optional, Sequence, Callable
from .validators import (
    convert_identifier,
    unwrap_underscore,
    DeepIterableConverter,
    ProxyInstanceOfValidator,
)


def unparse(node: Node) -> str:
    tree = to_builtin(node)
    tree = ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def parse(text: str) -> Node:
    tree = ast.parse(text)
    return from_builtin(tree)


class Node:
    pass


def to_builtin(node: Node):
    assert isinstance(node, Node)
    return node._to_builtin()


def from_builtin(node: ast.AST) -> Node:
    assert isinstance(node, ast.AST)
    t = node.__class__.__name__
    return NODES[t]._from_builtin(node)

@attrs.define
class TransformerContext:
    parents: Sequence[Node] = attrs.field(factory=list)

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
