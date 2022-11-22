from itertools import chain
from pathlib import Path

import attrs

import mk_helpers
from activated_wast import _, get_fragment, w, unparse
from upstream import asdl, dfns


def mk_io_validator(val):
    return _.ProxyInstanceOfValidator(w.Lambda(w.arguments(), val))


def const(val):
    return w.Constant(val)


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
                return w.IfExp(
                    body=const(None),
                    orelse=mk_fn(value_expr),
                    test=w.Compare(
                        left=value_expr, comparators=[const(None)], ops=[w.Is()]
                    ),
                )
            elif self.seq:
                return w.ListComp(
                    elt=mk_fn(_.x),
                    generators=[
                        w.comprehension(is_async=0, iter=value_expr, target=_.x)
                    ],
                )
            else:
                return mk_fn(value_expr)
        else:
            return value_expr

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
                converters += [_.unwrap_node]
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
                converter = _.attrs.converters.pipe(*converters)
            else:
                converter = first

        field_args = {}
        if spec.opt:
            annotation = _.Optional[annotation]

            if validators:
                field_args |= dict(validator=_.attrs.validators.optional(validator))

            if converters:
                field_args |= dict(converter=_.attrs.converters.optional(converter))

            field_args |= dict(default=w.Constant(None))
        elif spec.seq:
            annotation = _.Sequence[annotation]

            if validators:
                field_args |= dict(
                    validator=_.attrs.validators.deep_iterable(validator)
                )

            if converters:
                converter = _.attrs.converters.pipe(_.unpack_nested, _.DeepIterableConverter(converter))
            else:
                converter = _.unpack_nested

            field_args |= dict(factory=_.tuple, converter=converter)
        else:
            if validators:
                field_args |= dict(validator=validator)

            if converters:
                field_args |= dict(converter=converter)

        if self.name in ("type_comment", "type_ignores"):
            field_args |= dict(repr=w.Constant(False))

        node = w.AnnAssign(
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

        return w.FunctionDef(
            name="_to_builtin",
            args=w.arguments(
                args=[w.arg(arg="self")],
            ),
            body=[w.Return(ret)],
        )

    @property
    def from_builtin(self):
        kwargs = {
            x.name: x.mk_transformer(_.node._(x.name), lambda x: _.from_builtin(x))
            for x in self.parsed_fields
        }
        ret = _.cls(**kwargs)

        return w.FunctionDef(
            name="_from_builtin",
            decorator_list=[_.classmethod],
            args=w.arguments(
                args=[w.arg(arg="cls"), w.arg(arg="node")],
            ),
            body=[w.Return(ret)],
        )

    @property
    def transform(self):
        inner_context = w.Assign(
            targets=[_.inner_context],
            value=_.TransformerContext(
                parents=w.List([_.self, w.Starred(_.context.parents)]),
                original=_.self,
            ),
        )
        kwargs = {
            x.name: x.mk_transformer(
                _.self._(x.name),
                lambda x: x._transform(_.node_transformer, _.inner_context),
            )
            for x in self.parsed_fields
        }
        transformed = w.Assign(targets=[_.transformed], value=_(self.name)(**kwargs))
        ret = _.node_transformer(_.transformed, _.context)

        return w.FunctionDef(
            name="_transform",
            args=w.arguments(
                args=[
                    w.arg(arg="self"),
                    w.arg(arg="node_transformer"),
                    w.arg(arg="context"),
                ],
            ),
            body=[inner_context, transformed, w.Return(ret)],
        )

    @property
    def rendered(self):
        node = w.ClassDef(
            decorator_list=[_.attrs.frozen()],
            bases=[_(self.base_name)],
            name=self.name,
            body=[
                *chain.from_iterable(x.rendered for x in self.parsed_fields),
                self.to_builtin,
                self.from_builtin,
                self.transform,
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
        base = w.ClassDef(
            bases=[_.Node],
            name=self.name,
            body=[w.Pass()],
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
        registry = w.Assign(
            value=_.dict(**{x.name: _(x.name) for x in self.nodes}),
            targets=[_.NODES],
        )
        return w.Module(
            [
                *get_fragment("header"),
                *chain.from_iterable(x.rendered for x in self.dfns_parsed),
                registry,
            ]
        )


nodes_tree = TopLevel(dfns=dfns).rendered
nodes_text = unparse(nodes_tree)
helpers_text = unparse(mk_helpers.tree)

Path("wast/nodes.py").write_text(nodes_text)
Path("wast/helpers.py").write_text(helpers_text)
