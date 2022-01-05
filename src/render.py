import asdl
import ast
import ast_utils as au
import warnings


def snake_to_camel(val):
    return "".join(x.title() for x in val.split("_"))


def render_product(name, spec):
    return [
        ast.ClassDef(
            decorator_list=[au.mk_attr_s(kw_only=ast.Constant(True))],
            bases=[],
            keywords=[],
            name=name,
            body=[render_field(x) for x in spec.fields],
        )
    ]


def render_construct(parent, spec):
    return ast.ClassDef(
        decorator_list=[au.mk_attr_s(kw_only=ast.Constant(True))],
        bases=[ast.Name(parent)],
        keywords=[],
        name=spec.name,
        body=[render_field(x) for x in spec.fields] or [ast.Pass()],
    )


def render_sum(parent, spec):
    parent = snake_to_camel(parent)
    base = ast.ClassDef(
        decorator_list=[au.mk_attr_s(kw_only=ast.Constant(True))],
        bases=[],
        keywords=[],
        name=parent,
        body=[ast.Pass()],
    )
    return [base] + [render_construct(parent, t) for t in spec.types]


def render_field(f):
    t = f.type

    if t == "identifier":
        raw = ast.Name("str")
        validators = [
            au.mk_io_validator(ast.Name("str")),
            ast.Name("validate_identifier"),
        ]
    elif t == "string":
        raw = ast.Name("str")
        validators = [au.mk_io_validator(ast.Name("str"))]
    elif t == "int":
        raw = ast.Name("int")
        validators = [au.mk_io_validator(ast.Name("int"))]
    else:
        name = snake_to_camel(f.type)
        raw = ast.Name(name)
        validators = [au.mk_io_validator(ast.Name(name))]

    if f.opt:
        annotation = au.mk_optional_type(raw)
        validator = au.mk_opt_validator(ast.List(validators))
        ib_args = dict(default=ast.Constant(None))
    elif f.seq:
        annotation = au.mk_seq_type(raw)
        validator = au.mk_seq_validator(*validators)
        ib_args = dict(default=ast.Name("list"))
    else:
        annotation = raw
        validator = ast.List(validators)
        ib_args = dict()

    return ast.AnnAssign(
        target=ast.Name(f.name),
        annotation=annotation,
        value=au.mk_attr_ib(validator=validator, **ib_args),
        simple=True,
    )


def render_type(t):
    if isinstance(t.value, asdl.Product):
        return render_product(t.name, t.value)
    elif isinstance(t.value, asdl.Sum):
        return render_sum(t.name, t.value)
    else:
        assert False


def render_ifs(entries):
    if not entries:
        return ast.Assert(ast.Constant(False), msg=None)

    our, *rest = entries
    dict_call = ast.Call(
        args=[],
        func=ast.Name(our['name']),
        keywords=[ast.keyword(arg=None, value=au.mk_aa('node', '__dict__'))],
    )

    return ast.If(
        test=ast.Call(
            args=[ast.Name("node"), au.mk_aa("ast", our["name"])],
            func=ast.Name("isinstance"),
            keywords=[],
        ),
        body=[ast.Return(dict_call)],
        orelse=[render_ifs(rest)],
    )


def render_converter(types):
    names = [x.name for x in types if isinstance(x.value, asdl.Product)]
    names += chain(*[[c.name for c in s.value.types] for s in types if isinstance(s.value, asdl.Sum)])
    return ast.FunctionDef(
        args=ast.arguments(
            args=[ast.arg(arg="node", annotation=None)],
            defaults=[],
            vararg=None,
            kwarg=None,
        ),
        body=[render_ifs([dict(name=n) for n in names])],
        name="from_built_in",
        decorator_list=[],
    )


dfns = asdl.parse("Python.asdl").dfns
import astor
from itertools import chain

body = sum((render_type(x) for x in dfns), start=[render_converter(dfns)])

b = '''
from __future__ import annotations
import ast
import attr as attrs
from typing import Optional, Sequence, Callable
from validators import *

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
'''
print(b + astor.to_source(ast.Module(body)))
