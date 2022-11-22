from __future__ import annotations

import ast
from typing import Any, Optional, Sequence

import attrs

from .common import Node, TransformerContext, WrappedNode
from .validators import (
    DeepIterableConverter,
    ProxyInstanceOfValidator,
    convert_identifier,
    unwrap_node,
    unpack_nested,
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
