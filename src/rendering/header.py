from __future__ import annotations
import ast
import attr as attrs
from typing import Optional, Sequence, Callable
from .validators import *

def unparse(node):
    n = ast.fix_missing_locations(node._to_builtin())
    return ast.unparse(n)

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


@attrs.attrs(repr=False, slots=True, hash=True)
class ProxyInstanceOfValidator(object):
    type: Callable[[], Any] = attrs.ib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        type=self.type()
        if not isinstance(value, type):
            raise TypeError(
                "'{name}' must be {type!r} (got {value!r} that is a "
                "{actual!r}).".format(
                    name=attr.name,
                    type=type,
                    actual=value.__class__,
                    value=value,
                ),
                attr,
                type,
                value,
            )

    def __repr__(self):
        return "<proxy_instance_of validator for type {type!r}>".format(
            type=self.type()
        )
