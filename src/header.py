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

    def __and__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=And(), right=other.__inner__)
        )

    def __floordiv__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=FloorDiv(), right=other.__inner__)
        )

    def __mod__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Mod(), right=other.__inner__)
        )

    def __lshift__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=LShift(), right=other.__inner__)
        )

    def __rshift__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=RShift(), right=other.__inner__)
        )

    def __matmul__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=MatMult(), right=other.__inner__)
        )

    def __sub__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Sub(), right=other.__inner__)
        )

    def __pow__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Mod(), right=other.__inner__)
        )

    def __div__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Div(), right=other.__inner__)
        )

    def __lt__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Lt()])
        )

    def __gt__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Gt()])
        )

    def __le__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Le()])
        )

    def __ge__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Ge()])
        )

    def __lt__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Lt()])
        )

    def __eq__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Eq()])
        )

    def __ne__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[NotEq()])
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = slice(lower=key.start, upper=key.stop, step=key.step)

        return BoundUnderscore(Subscript(slice=key, value=self.__inner__))

    @property
    def _(self):
        return self.__inner__
