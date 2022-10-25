import asdl
import attrs
from activated_wast import w, _
from itertools import chain
from fragments import FRAGMENTS


def mk_io_validator(val):
    return _.ProxyInstanceOfValidator(w.Lambda(w.arguments(), val))._


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
    def has_default(self):
        return self.spec.opt or self.spec.seq

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
                validators += [mk_io_validator(annotation)]

        assert len(validators) < 2  # FIXME

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
        key = f"class_suffix_{self.name}"
        try:
            return [FRAGMENTS[key]]
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
            x.name: _.wast_to_node(_.self._(x.name)._)._ for x in self.parsed_fields
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
            x.name: _.node_to_wast(_.node._(x.name)._)._ for x in self.parsed_fields
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
    def rendered(self):
        node = w.ClassDef(
            decorator_list=[
                _.attrs.define(hash=const(True), slots=const(True), eq=const(True))._
            ],
            bases=[_(self.base_name)._],
            name=self.name,
            body=[
                *chain.from_iterable(x.rendered for x in self.parsed_fields),
                self.to_builtin,
                self.from_builtin,
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
    def rendered(self):
        nodes = list(chain.from_iterable(x.rendered for x in self.dfns_parsed))
        return w.Module(nodes)


dfns = asdl.parse("Python.asdl").dfns
top_level = TopLevel(dfns=dfns)
header = "".join(open("header.py", "r"))
rendered = top_level.rendered

print(header + w.unparse(rendered))
