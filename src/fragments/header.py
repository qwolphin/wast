from __future__ import annotations

import ast
from typing import Callable, Optional, Sequence, Union

import attrs

from .common import Node, WrappedNode, TransformerContext
from .validators import (
    DeepIterableConverter,
    ProxyInstanceOfValidator,
    convert_identifier,
    unwrap_underscore,
)


def to_builtin(node: Node) -> ast.AST:
    match node:
        case WrappedNode():
            node = node.__inner__
        case Node():
            pass
        case other:
            raise TypeError("Wrong type")

    return node._to_builtin()


def from_builtin(node: ast.AST) -> Node:
    assert isinstance(node, ast.AST)
    t = node.__class__.__name__
    return NODES[t]._from_builtin(node)


class Node:
    pass
