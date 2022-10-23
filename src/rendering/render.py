import asdl
import ast
import ast_utils as au
import warnings
import attrs
import astor
from itertools import chain
import stable.wast as wast

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
        return self.spec.opt or self.spec.seq or self.type == "expr_context"

    @property
    def rendered(self):
        spec = self.spec

        validators = []
        match self.type:
            case "identifier":
                raw = ast.Name("str")
            case "string":
                raw = ast.Name("str")
                validators += [au.mk_io_validator(ast.Name("str"))]
            case "int":
                raw = ast.Name("int")
                validators += [au.mk_io_validator(ast.Name("int"))]
            case "constant":
                raw = ast.Name("Any")
            case _:
                raw = ast.Name(self.type)
                validators += [au.mk_io_validator(raw)]

        field_args = {}
        if spec.opt:
            annotation = au.mk_optional_type(raw)

            if validators:
                field_args |= dict(validator=au.mk_opt_validator(ast.List(validators)))

            field_args |= dict(default=ast.Constant(None))
        elif spec.seq:
            annotation = au.mk_seq_type(raw)

            if validators:
                field_args |= dict(validator=au.mk_seq_validator(*validators))

            field_args |= dict(factory=ast.Name("list"))
        else:
            annotation = raw

            if validators:
                field_args |= dict(validator=ast.List(validators))

        if self.name in ("type_comment", "type_ignores"):
            field_args |= dict(repr=ast.Constant(False))

        node = ast.AnnAssign(
            target=ast.Name(self.name),
            annotation=annotation,
            value=au.mk_attr_ib(**field_args),
            simple=True,
        )
        return [node]


class FieldsMixin:
    @property
    def parsed_fields(self):
        return sorted((Field(x) for x in self.spec.fields if x.type != "expr_context"), key=lambda x: (x.has_default, x.name))

    def builtin_call(self, source_name, target_expr, fn):
        return ast.Call(
            func=target_expr,
            args=[],
            keywords=[
                ast.keyword(
                    arg=f.name,
                    value=ast.Call(func=ast.Name(fn), args=[au.mk_aa(source_name, f.name)], keywords=[]),
                )
                for f in self.parsed_fields
            ],
        )

    @property
    def rendered(self):
        to_builtin = ast.FunctionDef(
            name="_to_builtin",
            decorator_list=[],
            args=ast.arguments(
                args=[
                    ast.arg(
                        arg="self",
                    )
                ],
                defaults=[],
                vararg=None,
                kwarg=None,
            ),
            keywords=[],
            body=[ast.Return(self.builtin_call("self", au.mk_aa("ast", self.name), "wast_to_node"))],
        )
        from_builtin = ast.FunctionDef(
            name="_from_builtin",
            decorator_list=[ast.Name("classmethod")],
            args=ast.arguments(
                args=[
                    ast.arg(
                        arg="cls",
                    ),
                    ast.arg(
                        arg="node",
                    ),
                ],
                defaults=[],
                vararg=None,
                kwarg=None,
            ),
            keywords=[],
            body=[ast.Return(self.builtin_call("node", ast.Name("cls"), "node_to_wast"))],
        )
        node = ast.ClassDef(
            decorator_list=[au.mk_attr_s(hash=ast.Constant(True), slots=ast.Constant(True), eq=ast.Constant(True))],
            bases=[ast.Name(self.base_name)],
            keywords=[],
            name=self.name,
            body=[*chain.from_iterable(x.rendered for x in self.parsed_fields), to_builtin, from_builtin],
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
    def parsed_constructors(self):
        return [Constructor(self.name, spec) for spec in self.spec.types]

    @property
    def rendered(self):
        base = ast.ClassDef(
            decorator_list=[],
            bases=[ast.Name("Node")],
            keywords=[],
            name=self.name,
            body=[ast.Pass()],
        )
        return [base, *chain.from_iterable(x.rendered for x in self.parsed_constructors)]


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
        return ast.Module(nodes)


dfns = asdl.parse("Python.asdl").dfns
top_level = TopLevel(dfns=dfns)
header = "".join(open("header.py", "r"))
rendered = top_level.rendered
#wast.node_to_wast(rendered)

print(header + astor.to_source(rendered))
