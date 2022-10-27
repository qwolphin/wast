import asdl
import attrs
from activated_wast import w, _
from itertools import chain
from fragments import FRAGMENTS, report_unused_fragments


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

    def mk_from_to_builtin(self, value_expr, fn_expr):
        if self.is_object:
            if self.opt:
                return w.IfExp(
                    body=const(None),
                    orelse=fn_expr()(value_expr)._,
                    test=w.Compare(
                        left=value_expr, comparators=[const(None)], ops=[w.Is()]
                    ),
                )
            elif self.seq:
                return w.ListComp(
                    elt=fn_expr()(_.x._)._,
                    generators=[
                        w.comprehension(is_async=0, iter=value_expr, target=_.x._)
                    ],
                )
            else:
                return fn_expr()(value_expr)._
        else:
            return value_expr

    @property
    def nodes_iter_entry(self):
        if not self.is_object:
            return []

        val = _.self._(self.name)._
        iter = val()._nodes_iter()._
        if self.opt:
            ret = w.If(
                test=w.Compare(left=val, comparators=[const(None)], ops=[w.IsNot()]),
                body=[w.Expr(w.YieldFrom(value=iter))],
            )
        elif self.seq:
            inner = w.If(
                test=w.Compare(left=_.x._, comparators=[const(None)], ops=[w.IsNot()]),
                body=[w.Expr(w.YieldFrom(value=_.x._nodes_iter()._))],
            )
            ret = w.For(iter=val, target=_.x._, body=[inner])

        else:
            ret = w.Expr(w.YieldFrom(value=iter))

        return [ret]

    @property
    def rendered(self):
        spec = self.spec

        validators = []
        converter = None
        match self.type:
            case "identifier":
                annotation = _.str._
                converter = _.convert_identifier._
            case "string":
                annotation = _.str._
                validators += [mk_io_validator(annotation)]
            case "int":
                annotation = _.int._
                validators += [mk_io_validator(annotation)]
            case "constant":
                annotation = _.Any._
            case _:
                annotation = _(self.type)._
                converter = _.unwrap_underscore._
                validators += [mk_io_validator(annotation)]

        assert len(validators) < 2  # fixme

        field_args = {}
        if spec.opt:
            annotation = _.Optional[annotation]._

            if validators:
                field_args |= dict(
                    validator=_.attrs.validators.optional(validators[0])._
                )

            # FIXME handle converter

            field_args |= dict(default=w.Constant(None))
        elif spec.seq:
            annotation = _.Sequence[annotation]._

            if validators:
                field_args |= dict(
                    validator=_.attrs.validators.deep_iterable(validators[0])._
                )

            if converter:
                converter = _.DeepIterableConverter(converter)._

            field_args |= dict(factory=_.list._)
        else:
            if validators:
                field_args |= dict(validator=validators[0])

        if self.name in ("type_comment", "type_ignores"):
            field_args |= dict(repr=w.Constant(False))

        if converter:
            field_args |= dict(converter=converter)

        node = w.AnnAssign(
            target=_(self.name)._,
            annotation=annotation,
            value=_.attrs.field(**field_args)._,
            simple=1,
        )
        return [node]


class ClassSuffixMixin:
    @property
    def class_suffix(self):
        key = f"class_suffix/{self.name}"
        try:
            return FRAGMENTS[key]
        except KeyError:
            return []


class FieldsMixin(ClassSuffixMixin):
    @property
    def parsed_fields(self):
        return sorted(
            (Field(x) for x in self.spec.fields if x.type != "expr_context"),
            key=lambda x: (x.has_default, x.name),
        )

    @property
    def to_builtin(self):
        kwargs = {
            x.name: x.mk_from_to_builtin(_.self._(x.name)._, _.to_builtin._)
            for x in self.parsed_fields
        }
        ret = _.ast._(self.name)(**kwargs)._

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
            x.name: x.mk_from_to_builtin(_.node._(x.name)._, _.from_builtin._)
            for x in self.parsed_fields
        }
        ret = _.cls(**kwargs)._

        return w.FunctionDef(
            name="_from_builtin",
            decorator_list=[_("classmethod")._],
            args=w.arguments(
                args=[w.arg(arg="cls"), w.arg(arg="node")],
            ),
            body=[w.Return(ret)],
        )

    @property
    def transform(self):
        kwargs = {
            x.name: x.mk_from_to_builtin(_.self._(x.name)._, _.node_transformer._)
            for x in self.parsed_fields
        }
        ret = _(self.name)(**kwargs)._

        return w.FunctionDef(
            name="_transform",
            args=w.arguments(
                args=[
                    w.arg(arg="self"),
                    w.arg(arg="node_transformer"),
                    w.arg(arg="context"),
                ],
            ),
            body=[w.Return(ret)],
        )

    @property
    def nodes_iter(self):
        body = [
            w.Expr(w.Yield(value=_.self._)),
            *chain.from_iterable(x.nodes_iter_entry for x in self.parsed_fields),
        ]
        return w.FunctionDef(
            name="_nodes_iter",
            args=w.arguments(
                args=[
                    w.arg(arg="self"),
                ],
            ),
            body=body,
        )

    @property
    def rendered(self):
        node = w.ClassDef(
            decorator_list=[_.attrs.define()._],
            bases=[_(self.base_name)._],
            name=self.name,
            body=[
                *chain.from_iterable(x.rendered for x in self.parsed_fields),
                self.to_builtin,
                self.from_builtin,
                self.transform,
                self.nodes_iter,
                *self.class_suffix,
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
class Sum(ClassSuffixMixin):
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
            bases=[_.Node._],
            name=self.name,
            body=self.class_suffix or [w.Pass()],
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
            value=_.dict(**{x.name: _(x.name)._ for x in self.nodes})._,
            targets=[_.NODES._],
        )
        return w.Module(
            [*chain.from_iterable(x.rendered for x in self.dfns_parsed), registry]
        )


dfns = asdl.parse("Python.asdl").dfns
top_level = TopLevel(dfns=dfns)
header = "".join(open("header.py", "r"))
rendered = top_level.rendered

print(header + w.unparse(rendered))

report_unused_fragments()
