from __future__ import annotations
import keyword
from typing import Union, Callable, Any

# from . import wast
from attrs import define, field


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
            converter=self.member_converter()
        )


def unwrap_underscore(value):
    if value.__class__.__name__ == "BoundUnderscore":
        return value.__inner__

    return value


def convert_identifier(value: Union[str | wast.Name]) -> str:
    match value:
        case str():
            val = value
        case wast.Name():
            val = value.id
        case _:
            raise TypeError(
                f"{val} has type {val.__class__}. Must be {str} or wast.Name"
            )

    if keyword.iskeyword(val):
        raise ValueError(f"{val} is a Python keyword")

    if val == "*" and not val.isidentifier():
        raise ValueError(f"{val} is not a valid Python identifier")

    return val
