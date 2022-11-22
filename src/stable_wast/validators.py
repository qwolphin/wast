from __future__ import annotations
from itertools import chain

import keyword
from typing import Any, Callable, Sequence, TypeVar

from attrs import define, field

from . import nodes as w


@define(repr=False)
class ProxyInstanceOfValidator(object):
    type: Callable[[], Any] = field()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        type = self.type()
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


@define(repr=False)
class DeepIterableConverter(object):
    member_converter: Callable[[Any], Any]  # FIXME

    def __call__(self, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        return [self.member_converter(x) for x in value]

    def __repr__(self):
        return "<deep_iterable converter using {converter!r}>".format(
            converter=self.member_converter
        )


def unwrap_node(value: w.WrappedNode | w.Node) -> w.Node:
    if isinstance(value, w.WrappedNode):
        return value.__inner__

    return value


T = TypeVar("T")


def unpack_nested(val: Sequence[T | tuple[T, ...] | list[T]]) -> list[T]:
    return list(
        chain.from_iterable(x if isinstance(x, (list, tuple)) else [x] for x in val)
    )


def convert_identifier(val: str | w.Name) -> str:
    match val:
        case str():
            pass
        case w.Name():
            val = val.id
        case other:
            raise TypeError(f"{val} has type {val.__class__}. Must be {str} or w.Name")

    if keyword.iskeyword(val):
        raise ValueError(f"{val} is a Python keyword")

    if not val.isidentifier() and val != "*":
        raise ValueError(f"{val} is not a valid Python identifier")

    return val
