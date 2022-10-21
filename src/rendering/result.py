from __future__ import annotations
import ast
import attr as attrs
from typing import Optional, Sequence, Callable
from validators import *


def unparse(node):
    return ast.unparse(node._to_builtin())


class Node:
    pass


def to_builtin(node):
    match node:
        case None:
            return None
        case list() | tuple():
            return [to_builtin(x) for x in node]
        case ast.Node:
            return globals()[node.__class__.__name__](**node.__dict__)
        case _:
            raise TypeError()

    assert isinstance(node, ast.Node)


@attrs.attrs(repr=False, slots=True, hash=True)
class ProxyInstanceOfValidator(object):
    type: Callable[[], Any] = attrs.ib()

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


class WastTrasnformerBase(ast.NodeTransformer):
    def generic_visit(self, node):
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node


class mod(Node):
    pass


@attrs.s(kw_only=True)
class Module(mod):
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    type_ignores: Sequence[type_ignore] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: type_ignore)
        ),
        default=list,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Module(body=self.body, type_ignores=self.type_ignores)


@attrs.s(kw_only=True)
class Interactive(mod):
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Interactive(body=self.body)


@attrs.s(kw_only=True)
class Expression(mod):
    body: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.Expression(body=self.body)


@attrs.s(kw_only=True)
class FunctionType(mod):
    argtypes: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    returns: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.FunctionType(argtypes=self.argtypes, returns=self.returns)


class stmt(Node):
    pass


@attrs.s(kw_only=True)
class FunctionDef(stmt):
    name: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    args: arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: arguments)])
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    decorator_list: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    returns: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.FunctionDef(
            name=self.name,
            args=self.args,
            body=self.body,
            decorator_list=self.decorator_list,
            returns=self.returns,
            type_comment=self.type_comment,
        )


@attrs.s(kw_only=True)
class AsyncFunctionDef(stmt):
    name: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    args: arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: arguments)])
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    decorator_list: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    returns: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncFunctionDef(
            name=self.name,
            args=self.args,
            body=self.body,
            decorator_list=self.decorator_list,
            returns=self.returns,
            type_comment=self.type_comment,
        )


@attrs.s(kw_only=True)
class ClassDef(stmt):
    name: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    bases: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    keywords: Sequence[keyword] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: keyword)
        ),
        default=list,
    )
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    decorator_list: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.ClassDef(
            name=self.name,
            bases=self.bases,
            keywords=self.keywords,
            body=self.body,
            decorator_list=self.decorator_list,
        )


@attrs.s(kw_only=True)
class Return(stmt):
    value: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.Return(value=self.value)


@attrs.s(kw_only=True)
class Delete(stmt):
    targets: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Delete(targets=self.targets)


@attrs.s(kw_only=True)
class Assign(stmt):
    targets: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Assign(
            targets=self.targets, value=self.value, type_comment=self.type_comment
        )


@attrs.s(kw_only=True)
class AugAssign(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    op: operator = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: operator)])
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.AugAssign(target=self.target, op=self.op, value=self.value)


@attrs.s(kw_only=True)
class AnnAssign(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    annotation: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    value: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    simple: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: int)])

    def _to_builtin(self):
        return ast.AnnAssign(
            target=self.target,
            annotation=self.annotation,
            value=self.value,
            simple=self.simple,
        )


@attrs.s(kw_only=True)
class For(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    iter: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    orelse: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.For(
            target=self.target,
            iter=self.iter,
            body=self.body,
            orelse=self.orelse,
            type_comment=self.type_comment,
        )


@attrs.s(kw_only=True)
class AsyncFor(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    iter: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    orelse: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncFor(
            target=self.target,
            iter=self.iter,
            body=self.body,
            orelse=self.orelse,
            type_comment=self.type_comment,
        )


@attrs.s(kw_only=True)
class While(stmt):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    orelse: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.While(test=self.test, body=self.body, orelse=self.orelse)


@attrs.s(kw_only=True)
class If(stmt):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    orelse: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.If(test=self.test, body=self.body, orelse=self.orelse)


@attrs.s(kw_only=True)
class With(stmt):
    items: Sequence[withitem] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: withitem)
        ),
        default=list,
    )
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.With(
            items=self.items, body=self.body, type_comment=self.type_comment
        )


@attrs.s(kw_only=True)
class AsyncWith(stmt):
    items: Sequence[withitem] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: withitem)
        ),
        default=list,
    )
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncWith(
            items=self.items, body=self.body, type_comment=self.type_comment
        )


@attrs.s(kw_only=True)
class Match(stmt):
    subject: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    cases: Sequence[match_case] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: match_case)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Match(subject=self.subject, cases=self.cases)


@attrs.s(kw_only=True)
class Raise(stmt):
    exc: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    cause: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.Raise(exc=self.exc, cause=self.cause)


@attrs.s(kw_only=True)
class Try(stmt):
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    handlers: Sequence[excepthandler] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: excepthandler)
        ),
        default=list,
    )
    orelse: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )
    finalbody: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Try(
            body=self.body,
            handlers=self.handlers,
            orelse=self.orelse,
            finalbody=self.finalbody,
        )


@attrs.s(kw_only=True)
class Assert(stmt):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    msg: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.Assert(test=self.test, msg=self.msg)


@attrs.s(kw_only=True)
class Import(stmt):
    names: Sequence[alias] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: alias)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Import(names=self.names)


@attrs.s(kw_only=True)
class ImportFrom(stmt):
    module: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )
    names: Sequence[alias] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: alias)
        ),
        default=list,
    )
    level: Optional[int] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: int)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.ImportFrom(module=self.module, names=self.names, level=self.level)


@attrs.s(kw_only=True)
class Global(stmt):
    names: Sequence[str] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            attrs.validators.and_(
                ProxyInstanceOfValidator(lambda: str), validate_identifier
            )
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Global(names=self.names)


@attrs.s(kw_only=True)
class Nonlocal(stmt):
    names: Sequence[str] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            attrs.validators.and_(
                ProxyInstanceOfValidator(lambda: str), validate_identifier
            )
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Nonlocal(names=self.names)


@attrs.s(kw_only=True)
class Expr(stmt):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.Expr(value=self.value)


@attrs.s(kw_only=True)
class Pass(stmt):
    def _to_builtin(self):
        return ast.Pass()


@attrs.s(kw_only=True)
class Break(stmt):
    def _to_builtin(self):
        return ast.Break()


@attrs.s(kw_only=True)
class Continue(stmt):
    def _to_builtin(self):
        return ast.Continue()


class expr(Node):
    pass


@attrs.s(kw_only=True)
class BoolOp(expr):
    op: boolop = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: boolop)])
    values: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.BoolOp(op=self.op, values=self.values)


@attrs.s(kw_only=True)
class NamedExpr(expr):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.NamedExpr(target=self.target, value=self.value)


@attrs.s(kw_only=True)
class BinOp(expr):
    left: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    op: operator = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: operator)])
    right: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.BinOp(left=self.left, op=self.op, right=self.right)


@attrs.s(kw_only=True)
class UnaryOp(expr):
    op: unaryop = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: unaryop)])
    operand: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.UnaryOp(op=self.op, operand=self.operand)


@attrs.s(kw_only=True)
class Lambda(expr):
    args: arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: arguments)])
    body: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.Lambda(args=self.args, body=self.body)


@attrs.s(kw_only=True)
class IfExp(expr):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    body: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    orelse: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.IfExp(test=self.test, body=self.body, orelse=self.orelse)


@attrs.s(kw_only=True)
class Dict(expr):
    keys: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    values: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Dict(keys=self.keys, values=self.values)


@attrs.s(kw_only=True)
class Set(expr):
    elts: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Set(elts=self.elts)


@attrs.s(kw_only=True)
class ListComp(expr):
    elt: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    generators: Sequence[comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.ListComp(elt=self.elt, generators=self.generators)


@attrs.s(kw_only=True)
class SetComp(expr):
    elt: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    generators: Sequence[comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.SetComp(elt=self.elt, generators=self.generators)


@attrs.s(kw_only=True)
class DictComp(expr):
    key: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    generators: Sequence[comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.DictComp(key=self.key, value=self.value, generators=self.generators)


@attrs.s(kw_only=True)
class GeneratorExp(expr):
    elt: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    generators: Sequence[comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.GeneratorExp(elt=self.elt, generators=self.generators)


@attrs.s(kw_only=True)
class Await(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.Await(value=self.value)


@attrs.s(kw_only=True)
class Yield(expr):
    value: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.Yield(value=self.value)


@attrs.s(kw_only=True)
class YieldFrom(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.YieldFrom(value=self.value)


@attrs.s(kw_only=True)
class Compare(expr):
    left: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    ops: Sequence[cmpop] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: cmpop)
        ),
        default=list,
    )
    comparators: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Compare(left=self.left, ops=self.ops, comparators=self.comparators)


@attrs.s(kw_only=True)
class Call(expr):
    func: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    args: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    keywords: Sequence[keyword] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: keyword)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.Call(func=self.func, args=self.args, keywords=self.keywords)


@attrs.s(kw_only=True)
class FormattedValue(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    conversion: Optional[int] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: int)]),
        default=None,
    )
    format_spec: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.FormattedValue(
            value=self.value, conversion=self.conversion, format_spec=self.format_spec
        )


@attrs.s(kw_only=True)
class JoinedStr(expr):
    values: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.JoinedStr(values=self.values)


@attrs.s(kw_only=True)
class Constant(expr):
    value: Any = attrs.ib(validator=[])
    kind: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.Constant(value=self.value, kind=self.kind)


@attrs.s(kw_only=True)
class Attribute(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    attr: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    ctx: Optional[expr_context] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: expr_context)]
        ),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Attribute(value=self.value, attr=self.attr, ctx=self.ctx)


@attrs.s(kw_only=True)
class Subscript(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    slice: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    ctx: Optional[expr_context] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: expr_context)]
        ),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Subscript(value=self.value, slice=self.slice, ctx=self.ctx)


@attrs.s(kw_only=True)
class Starred(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    ctx: Optional[expr_context] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: expr_context)]
        ),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Starred(value=self.value, ctx=self.ctx)


@attrs.s(kw_only=True)
class Name(expr):
    id: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    ctx: Optional[expr_context] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: expr_context)]
        ),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Name(id=self.id, ctx=self.ctx)


@attrs.s(kw_only=True)
class List(expr):
    elts: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    ctx: Optional[expr_context] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: expr_context)]
        ),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.List(elts=self.elts, ctx=self.ctx)


@attrs.s(kw_only=True)
class Tuple(expr):
    elts: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    ctx: Optional[expr_context] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: expr_context)]
        ),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Tuple(elts=self.elts, ctx=self.ctx)


@attrs.s(kw_only=True)
class Slice(expr):
    lower: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    upper: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    step: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )

    def _to_builtin(self):
        return ast.Slice(lower=self.lower, upper=self.upper, step=self.step)


class expr_context(Node):
    pass


@attrs.s(kw_only=True)
class Load(expr_context):
    def _to_builtin(self):
        return ast.Load()


@attrs.s(kw_only=True)
class Store(expr_context):
    def _to_builtin(self):
        return ast.Store()


@attrs.s(kw_only=True)
class Del(expr_context):
    def _to_builtin(self):
        return ast.Del()


class boolop(Node):
    pass


@attrs.s(kw_only=True)
class And(boolop):
    def _to_builtin(self):
        return ast.And()


@attrs.s(kw_only=True)
class Or(boolop):
    def _to_builtin(self):
        return ast.Or()


class operator(Node):
    pass


@attrs.s(kw_only=True)
class Add(operator):
    def _to_builtin(self):
        return ast.Add()


@attrs.s(kw_only=True)
class Sub(operator):
    def _to_builtin(self):
        return ast.Sub()


@attrs.s(kw_only=True)
class Mult(operator):
    def _to_builtin(self):
        return ast.Mult()


@attrs.s(kw_only=True)
class MatMult(operator):
    def _to_builtin(self):
        return ast.MatMult()


@attrs.s(kw_only=True)
class Div(operator):
    def _to_builtin(self):
        return ast.Div()


@attrs.s(kw_only=True)
class Mod(operator):
    def _to_builtin(self):
        return ast.Mod()


@attrs.s(kw_only=True)
class Pow(operator):
    def _to_builtin(self):
        return ast.Pow()


@attrs.s(kw_only=True)
class LShift(operator):
    def _to_builtin(self):
        return ast.LShift()


@attrs.s(kw_only=True)
class RShift(operator):
    def _to_builtin(self):
        return ast.RShift()


@attrs.s(kw_only=True)
class BitOr(operator):
    def _to_builtin(self):
        return ast.BitOr()


@attrs.s(kw_only=True)
class BitXor(operator):
    def _to_builtin(self):
        return ast.BitXor()


@attrs.s(kw_only=True)
class BitAnd(operator):
    def _to_builtin(self):
        return ast.BitAnd()


@attrs.s(kw_only=True)
class FloorDiv(operator):
    def _to_builtin(self):
        return ast.FloorDiv()


class unaryop(Node):
    pass


@attrs.s(kw_only=True)
class Invert(unaryop):
    def _to_builtin(self):
        return ast.Invert()


@attrs.s(kw_only=True)
class Not(unaryop):
    def _to_builtin(self):
        return ast.Not()


@attrs.s(kw_only=True)
class UAdd(unaryop):
    def _to_builtin(self):
        return ast.UAdd()


@attrs.s(kw_only=True)
class USub(unaryop):
    def _to_builtin(self):
        return ast.USub()


class cmpop(Node):
    pass


@attrs.s(kw_only=True)
class Eq(cmpop):
    def _to_builtin(self):
        return ast.Eq()


@attrs.s(kw_only=True)
class NotEq(cmpop):
    def _to_builtin(self):
        return ast.NotEq()


@attrs.s(kw_only=True)
class Lt(cmpop):
    def _to_builtin(self):
        return ast.Lt()


@attrs.s(kw_only=True)
class LtE(cmpop):
    def _to_builtin(self):
        return ast.LtE()


@attrs.s(kw_only=True)
class Gt(cmpop):
    def _to_builtin(self):
        return ast.Gt()


@attrs.s(kw_only=True)
class GtE(cmpop):
    def _to_builtin(self):
        return ast.GtE()


@attrs.s(kw_only=True)
class Is(cmpop):
    def _to_builtin(self):
        return ast.Is()


@attrs.s(kw_only=True)
class IsNot(cmpop):
    def _to_builtin(self):
        return ast.IsNot()


@attrs.s(kw_only=True)
class In(cmpop):
    def _to_builtin(self):
        return ast.In()


@attrs.s(kw_only=True)
class NotIn(cmpop):
    def _to_builtin(self):
        return ast.NotIn()


@attrs.s(kw_only=True)
class comprehension(Node):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    iter: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    ifs: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    is_async: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: int)])


class excepthandler(Node):
    pass


@attrs.s(kw_only=True)
class ExceptHandler(excepthandler):
    type: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    name: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.ExceptHandler(type=self.type, name=self.name, body=self.body)


@attrs.s(kw_only=True)
class arguments(Node):
    posonlyargs: Sequence[arg] = attrs.ib(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        default=list,
    )
    args: Sequence[arg] = attrs.ib(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        default=list,
    )
    vararg: Optional[arg] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: arg)]),
        default=None,
    )
    kwonlyargs: Sequence[arg] = attrs.ib(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        default=list,
    )
    kw_defaults: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    kwarg: Optional[arg] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: arg)]),
        default=None,
    )
    defaults: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class arg(Node):
    arg: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    annotation: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
        repr=False,
    )


@attrs.s(kw_only=True)
class keyword(Node):
    arg: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])


@attrs.s(kw_only=True)
class alias(Node):
    name: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    asname: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )


@attrs.s(kw_only=True)
class withitem(Node):
    context_expr: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    optional_vars: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class match_case(Node):
    pattern: pattern = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: pattern)])
    guard: Optional[expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: expr)]),
        default=None,
    )
    body: Sequence[stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        default=list,
    )


class pattern(Node):
    pass


@attrs.s(kw_only=True)
class MatchValue(pattern):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])

    def _to_builtin(self):
        return ast.MatchValue(value=self.value)


@attrs.s(kw_only=True)
class MatchSingleton(pattern):
    value: Any = attrs.ib(validator=[])

    def _to_builtin(self):
        return ast.MatchSingleton(value=self.value)


@attrs.s(kw_only=True)
class MatchSequence(pattern):
    patterns: Sequence[pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.MatchSequence(patterns=self.patterns)


@attrs.s(kw_only=True)
class MatchMapping(pattern):
    keys: Sequence[expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        default=list,
    )
    patterns: Sequence[pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        default=list,
    )
    rest: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )

    def _to_builtin(self):
        return ast.MatchMapping(keys=self.keys, patterns=self.patterns, rest=self.rest)


@attrs.s(kw_only=True)
class MatchClass(pattern):
    cls: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: expr)])
    patterns: Sequence[pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        default=list,
    )
    kwd_attrs: Sequence[str] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            attrs.validators.and_(
                ProxyInstanceOfValidator(lambda: str), validate_identifier
            )
        ),
        default=list,
    )
    kwd_patterns: Sequence[pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.MatchClass(
            cls=self.cls,
            patterns=self.patterns,
            kwd_attrs=self.kwd_attrs,
            kwd_patterns=self.kwd_patterns,
        )


@attrs.s(kw_only=True)
class MatchStar(pattern):
    name: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )

    def _to_builtin(self):
        return ast.MatchStar(name=self.name)


@attrs.s(kw_only=True)
class MatchAs(pattern):
    pattern: Optional[pattern] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: pattern)]
        ),
        default=None,
    )
    name: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )

    def _to_builtin(self):
        return ast.MatchAs(pattern=self.pattern, name=self.name)


@attrs.s(kw_only=True)
class MatchOr(pattern):
    patterns: Sequence[pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        default=list,
    )

    def _to_builtin(self):
        return ast.MatchOr(patterns=self.patterns)


class type_ignore(Node):
    pass


@attrs.s(kw_only=True)
class TypeIgnore(type_ignore):
    lineno: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: int)])
    tag: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: str)])

    def _to_builtin(self):
        return ast.TypeIgnore(lineno=self.lineno, tag=self.tag)
