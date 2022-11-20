from itertools import chain
from pathlib import Path

import attrs

import asdl
import operator_overloads
from activated_wast import _, n, wast
from fragments import get_fragment, report_unused_fragments


def mk_io_validator(val):
    return _.ProxyInstanceOfValidator(n.Lambda(n.arguments(), val))


def const(val):
    return n.Constant(val)


@attrs.define
class Field:
    spec: asdl.Field

    @property
    def name(self):
        return self.spec.name

    @property
    def type(self):
        return self.spec.type

    @property
    def opt(self):
        return self.spec.opt

    @property
    def seq(self):
        return self.spec.seq

    @property
    def has_default(self):
        return self.opt or self.seq

    @property
    def is_object(self):
        return self.type not in {"identifier", "string", "int", "constant"}

    def mk_transformer(self, value_expr, mk_fn):
        if self.is_object:
            if self.opt:
                return n.IfExp(
                    body=const(None),
                    orelse=mk_fn(value_expr),
                    test=n.Compare(
                        left=value_expr, comparators=[const(None)], ops=[n.Is()]
                    ),
                )
            elif self.seq:
                return n.ListComp(
                    elt=mk_fn(_.x),
                    generators=[
                        n.comprehension(is_async=0, iter=value_expr, target=_.x)
                    ],
                )
            else:
                return mk_fn(value_expr)
        else:
            return value_expr

    @property
    def nodes_iter_entry(self):
        if not self.is_object:
            return []

        val = _.self._(self.name)
        iter = val()._children()
        if self.opt:
            ret = n.If(
                test=n.Compare(left=val, comparators=[const(None)], ops=[n.IsNot()]),
                body=[n.Expr(n.YieldFrom(value=iter))],
            )
        elif self.seq:
            inner = n.If(
                test=n.Compare(left=_.x, comparators=[const(None)], ops=[n.IsNot()]),
                body=[n.Expr(n.YieldFrom(value=_.x._children()))],
            )
            ret = n.For(iter=val, target=_.x, body=[inner])

        else:
            ret = n.Expr(n.YieldFrom(value=iter))

        return [ret]

    @property
    def rendered(self):
        spec = self.spec

        validators = []
        converters = []
        match self.type:
            case "identifier":
                annotation = _.str
                converters += [_.convert_identifier]
            case "string":
                annotation = _.str
                validators += [mk_io_validator(annotation)]
            case "int":
                annotation = _.int
                validators += [mk_io_validator(annotation)]
            case "constant":
                annotation = _.Any
            case _:
                annotation = _(self.type)
                converters += [_.unwrap_underscore]
                validators += [mk_io_validator(annotation)]

        if validators:
            first, *rest = validators

            if rest:
                validator = _.attrs.validators.and_(*validators)
            else:
                validator = first

        if converters:
            first, *rest = converters

            if rest:
                converter = _.attrs.converter.pipe(*converters)
            else:
                converter = first

        field_args = {}
        if spec.opt:
            annotation = _.Optional[annotation]

            if validators:
                field_args |= dict(validator=_.attrs.validators.optional(validator))

            if converters:
                field_args |= dict(converter=_.attrs.converters.optional(converter))

            field_args |= dict(default=n.Constant(None))
        elif spec.seq:
            annotation = _.Sequence[annotation]

            if validators:
                field_args |= dict(
                    validator=_.attrs.validators.deep_iterable(validator)
                )

            if converters:
                field_args |= dict(converter=_.DeepIterableConverter(converter))

            field_args |= dict(factory=_.list)
        else:
            if validators:
                field_args |= dict(validator=validator)

            if converters:
                field_args |= dict(converter=converter)

        if self.name in ("type_comment", "type_ignores"):
            field_args |= dict(repr=n.Constant(False))

        node = n.AnnAssign(
            target=_(self.name),
            annotation=annotation,
            value=_.attrs.field(**field_args),
            simple=1,
        )
        return [node]


class FieldsMixin:
    @property
    def parsed_fields(self):
        return sorted(
            (Field(x) for x in self.spec.fields if x.type != "expr_context"),
            key=lambda x: (x.has_default, x.name),
        )

    @property
    def to_builtin(self):
        kwargs = {
            x.name: x.mk_transformer(_.self._(x.name), lambda x: _.to_builtin(x))
            for x in self.parsed_fields
        }
        ret = _.ast._(self.name)(**kwargs)

        return n.FunctionDef(
            name="_to_builtin",
            args=n.arguments(
                args=[n.arg(arg="self")],
            ),
            body=[n.Return(ret)],
        )

    @property
    def from_builtin(self):
        kwargs = {
            x.name: x.mk_transformer(_.node._(x.name), lambda x: _.from_builtin(x))
            for x in self.parsed_fields
        }
        ret = _.cls(**kwargs)

        return n.FunctionDef(
            name="_from_builtin",
            decorator_list=[_.classmethod],
            args=n.arguments(
                args=[n.arg(arg="cls"), n.arg(arg="node")],
            ),
            body=[n.Return(ret)],
        )

    @property
    def transform(self):
        inner_context = n.Assign(
            targets=[_.inner_context],
            value=_.TransformerContext(
                parents=n.List([_.self, n.Starred(_.context.parents)])
            ),
        )
        kwargs = {
            x.name: x.mk_transformer(
                _.self._(x.name),
                lambda x: x._transform(_.node_transformer, _.inner_context),
            )
            for x in self.parsed_fields
        }
        transformed = n.Assign(targets=[_.transformed], value=_(self.name)(**kwargs))
        ret = _.node_transformer(_.transformed, _.context)

        return n.FunctionDef(
            name="_transform",
            args=n.arguments(
                args=[
                    n.arg(arg="self"),
                    n.arg(arg="node_transformer"),
                    n.arg(arg="context"),
                ],
            ),
            body=[inner_context, transformed, n.Return(ret)],
        )

    @property
    def nodes_iter(self):
        body = [
            n.Expr(n.Yield(value=_.self)),
            *chain.from_iterable(x.nodes_iter_entry for x in self.parsed_fields),
        ]
        return n.FunctionDef(
            name="_children",
            args=n.arguments(
                args=[
                    n.arg(arg="self"),
                ],
            ),
            body=body,
        )

    @property
    def rendered(self):
        node = n.ClassDef(
            decorator_list=[_.attrs.frozen()],
            bases=[_(self.base_name)],
            name=self.name,
            body=[
                *chain.from_iterable(x.rendered for x in self.parsed_fields),
                self.to_builtin,
                self.from_builtin,
                self.transform,
                self.nodes_iter,
            ],
        )
        return [node]


@attrs.define
class Constructor(FieldsMixin):
    parent_name: str
    spec: asdl.Constructor

    @property
    def name(self):
        return self.spec.name

    @property
    def base_name(self):
        return self.parent_name


@attrs.define
class Sum:
    name: str
    spec: asdl.Sum

    @property
    def nodes(self):
        return self.parsed_constructors

    @property
    def parsed_constructors(self):
        return [Constructor(self.name, spec) for spec in self.spec.types]

    @property
    def rendered(self):
        base = n.ClassDef(
            bases=[_.Node],
            name=self.name,
            body=[n.Pass()],
        )
        return [
            base,
            *chain.from_iterable(x.rendered for x in self.parsed_constructors),
        ]


@attrs.define
class Product(FieldsMixin):
    name: str
    spec: asdl.Product

    @property
    def nodes(self):
        return [self]

    @property
    def base_name(self):
        return "Node"


@attrs.define
class TopLevel:
    dfns: list

    @staticmethod
    def parse_dfn(name, spec):
        match spec:
            case asdl.Sum():
                return Sum(name, spec)
            case asdl.Product():
                return Product(name, spec)
            case _:
                raise TypeError()

    @property
    def dfns_parsed(self):
        return [self.parse_dfn(x.name, x.value) for x in self.dfns]

    @property
    def nodes(self):
        return [*chain.from_iterable(x.nodes for x in self.dfns_parsed)]

    @property
    def rendered(self):
        registry = n.Assign(
            value=_.dict(**{x.name: _(x.name) for x in self.nodes}),
            targets=[_.NODES],
        )
        return n.Module(
            [
                *get_fragment("header"),
                *chain.from_iterable(x.rendered for x in self.dfns_parsed),
                registry,
            ]
        )


dfns = asdl.parse("Python.asdl").dfns
nodes_tree = TopLevel(dfns=dfns).rendered
nodes_text = wast.unparse(nodes_tree)

"""
from helpers import transformer

@transformer(filter=lambda e, c: n == n.Expr(n.Name('___operator_overloads')))
def asdf(e, c):
    return operator_overloads.methods
"""

Path("dev/wast.py").write_text(nodes_text)
