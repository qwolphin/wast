from functools import wraps
from inspect import signature
from typing import Callable, Optional, Sequence, Type, Union

import attrs

from .wast import Node, TransformerContext


@attrs.define
class transformer:
    # FIXME types
    type: Sequence[Type[Node]] = tuple()
    include: Sequence[Callable[[Node], bool]] = tuple()
    exclude: Sequence[Callable[[Node], bool]] = tuple()

    def __call__(self, f):
        @wraps(f)
        def ret(node, context):
            if self.type:
                if not isinstance(node, self.type):
                    return node

            if self.include:
                if not any(fn(node, context) for fn in self.include):
                    return node

            if any(fn(node, context) for fn in self.exclude):
                return node

            return f(node, context)

        return ret
