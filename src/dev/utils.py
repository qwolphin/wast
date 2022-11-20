import ast
from functools import wraps
from inspect import signature
from typing import Callable, Optional, Sequence, Type, Union

import attrs

from .common import Node, WrappedNode, TransformerContext
from .wast import from_builtin, to_builtin


def unparse(node: Node) -> str:
    tree = to_builtin(node)
    tree = ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def parse(text: str) -> Node:
    tree = ast.parse(text)
    return from_builtin(tree)



def transform(node: Node, fn) -> Node:
    assert isinstance(node, Node)
    ctx = TransformerContext(parents=tuple(), original=node)
    return node._transform(fn, ctx)


NT = Type[Node]
FnParams = [Node, TransformerContext]
FilterFn = Callable[FnParams, bool]
TransformerFn = Callable[FnParams, Node]


@attrs.define
class _transformer:
    """
    Class representing transformer containing zero or more functions
    """

    funcs: tuple[TransformerFn] = attrs.field(converter=tuple)

    def __or__(self, other):
        assert isinstance(other, _transformer)
        return _transformer([*self.funcs, *other.funcs])

    def __call__(self, node, context):
        for fn in self.funcs:
            node = fn(node, context)

        return node


@attrs.define
class transformer:
    """
    Decorator adding selectors to transformer functions, also allows chaining them like `fn1 | fn1`
    """

    type: tuple[NT] | NT | None = None
    filter: FilterFn | None = None
    exclude: FilterFn | None = None

    def __call__(self, f: TransformerFn) -> TransformerFn:
        @wraps(f)
        def ret(node, context):
            if self.type is not None:
                if not isinstance(node, self.type):
                    return node

            if self.filter is not None:
                if not self.filter(node, context):
                    return node

            if self.exclude is not None:
                if self.exclude(node, context):
                    return node

            return f(node, context)

        return _transformer([ret])
