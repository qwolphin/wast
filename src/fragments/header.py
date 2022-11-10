from __future__ import annotations
import ast
import attrs
from typing import Optional, Sequence, Callable, Union
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


def transform(node: Node, fn) -> Node:
    assert isinstance(node, Node)
    return node._transform(fn, TransformerContext())


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

    def __getitem__(self, key):
        return Constant(key)


_ = FreeUnderscore()
