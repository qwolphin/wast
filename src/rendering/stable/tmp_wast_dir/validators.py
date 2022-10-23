from __future__ import annotations
import keyword
from typing import Union, Callable, Any
from . import wast
from attrs import define, field
def validate_identifier(*args, **kwargs): pass
@define(repr=False)
class DeepIterableConverter(object):
    member_converter: Callable[[Any], Any] # FIXME

    def __call__(self, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        return [self.member_converter(x) for x in value]

    def __repr__(self):
        return "<deep_iterable converter using {converter!r}>".format(
            converter=self.member_converter()
        )


def convert_identifier(value: Union[str | wast.Name]) -> str:
    match value:
        case str():
            val = value
        case wast.Name():
            val = value.id
        case _:
            raise TypeError(f'{val} has type {val.__class__}. Must be {str} or {wast.Name}')

    if keyword.iskeyword(val):
        raise ValueError(f"{val} is a Python keyword")

    if val == "*":
        #import alias special case
        return

    if not val.isidentifier():
        raise ValueError(f"{val} is not a valid Python identifier")
