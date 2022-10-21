from __future__ import annotations
import ast
import attr as attrs
from typing import Optional, Sequence, Callable
from validators import *

def unparse(node):
    n = ast.fix_missing_locations(node._to_builtin())
    return ast.unparse(n)

class Node:
    pass

def node_to_wast(node):
    match node:
        case int() | float() | str() | None:
            return node
        case list() | tuple():
            return [node_to_wast(x) for x in node]
        case _:
            return globals()[node.__class__.__name__]._from_builtin(node)

def wast_to_node(node):
    match node:
        case int() | float() | str() | None:
            return node
        case list() | tuple():
            return [wast_to_node(x) for x in node]
        case _:
            return node._to_builtin()

@attrs.attrs(repr=False, slots=True, hash=True)
class ProxyInstanceOfValidator(object):
    type: Callable[[], Any] = attrs.ib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        type = self.type()
        if not isinstance(value, type):
            raise TypeError("'{name}' must be {type!r} (got {value!r} that is a {actual!r}).".format(name=attr.name, type=type, actual=value.__class__, value=value), attr, type, value)

    def __repr__(self):
        return '<proxy_instance_of validator for type {type!r}>'.format(type=self.type())

class mod(Node):
    pass

@attrs.s(kw_only=True)
class Module(mod):
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    type_ignores: Sequence[type_ignore] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : type_ignore)), default=list, repr=False)

    def _to_builtin(self):
        return ast.Module(body=wast_to_node(self.body), type_ignores=wast_to_node(self.type_ignores))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=node_to_wast(node.body), type_ignores=node_to_wast(node.type_ignores))

@attrs.s(kw_only=True)
class Interactive(mod):
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)

    def _to_builtin(self):
        return ast.Interactive(body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=node_to_wast(node.body))

@attrs.s(kw_only=True)
class Expression(mod):
    body: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.Expression(body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=node_to_wast(node.body))

@attrs.s(kw_only=True)
class FunctionType(mod):
    argtypes: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    returns: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.FunctionType(argtypes=wast_to_node(self.argtypes), returns=wast_to_node(self.returns))

    @classmethod
    def _from_builtin(cls, node):
        return cls(argtypes=node_to_wast(node.argtypes), returns=node_to_wast(node.returns))

class stmt(Node):
    pass

@attrs.s(kw_only=True)
class FunctionDef(stmt):
    name: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str), validate_identifier])
    args: arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : arguments)])
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    decorator_list: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    returns: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.FunctionDef(name=wast_to_node(self.name), args=wast_to_node(self.args), body=wast_to_node(self.body), decorator_list=wast_to_node(self.decorator_list), returns=wast_to_node(self.returns), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name), args=node_to_wast(node.args), body=node_to_wast(node.body), decorator_list=node_to_wast(node.decorator_list), returns=node_to_wast(node.returns), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class AsyncFunctionDef(stmt):
    name: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str), validate_identifier])
    args: arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : arguments)])
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    decorator_list: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    returns: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.AsyncFunctionDef(name=wast_to_node(self.name), args=wast_to_node(self.args), body=wast_to_node(self.body), decorator_list=wast_to_node(self.decorator_list), returns=wast_to_node(self.returns), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name), args=node_to_wast(node.args), body=node_to_wast(node.body), decorator_list=node_to_wast(node.decorator_list), returns=node_to_wast(node.returns), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class ClassDef(stmt):
    name: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str), validate_identifier])
    bases: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    keywords: Sequence[keyword] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : keyword)), default=list)
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    decorator_list: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.ClassDef(name=wast_to_node(self.name), bases=wast_to_node(self.bases), keywords=wast_to_node(self.keywords), body=wast_to_node(self.body), decorator_list=wast_to_node(self.decorator_list))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name), bases=node_to_wast(node.bases), keywords=node_to_wast(node.keywords), body=node_to_wast(node.body), decorator_list=node_to_wast(node.decorator_list))

@attrs.s(kw_only=True)
class Return(stmt):
    value: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)

    def _to_builtin(self):
        return ast.Return(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class Delete(stmt):
    targets: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.Delete(targets=wast_to_node(self.targets))

    @classmethod
    def _from_builtin(cls, node):
        return cls(targets=node_to_wast(node.targets))

@attrs.s(kw_only=True)
class Assign(stmt):
    targets: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.Assign(targets=wast_to_node(self.targets), value=wast_to_node(self.value), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(targets=node_to_wast(node.targets), value=node_to_wast(node.value), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class AugAssign(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    op: operator = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : operator)])
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.AugAssign(target=wast_to_node(self.target), op=wast_to_node(self.op), value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=node_to_wast(node.target), op=node_to_wast(node.op), value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class AnnAssign(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    annotation: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    value: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    simple: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : int)])

    def _to_builtin(self):
        return ast.AnnAssign(target=wast_to_node(self.target), annotation=wast_to_node(self.annotation), value=wast_to_node(self.value), simple=wast_to_node(self.simple))

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=node_to_wast(node.target), annotation=node_to_wast(node.annotation), value=node_to_wast(node.value), simple=node_to_wast(node.simple))

@attrs.s(kw_only=True)
class For(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    iter: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    orelse: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.For(target=wast_to_node(self.target), iter=wast_to_node(self.iter), body=wast_to_node(self.body), orelse=wast_to_node(self.orelse), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=node_to_wast(node.target), iter=node_to_wast(node.iter), body=node_to_wast(node.body), orelse=node_to_wast(node.orelse), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class AsyncFor(stmt):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    iter: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    orelse: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.AsyncFor(target=wast_to_node(self.target), iter=wast_to_node(self.iter), body=wast_to_node(self.body), orelse=wast_to_node(self.orelse), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=node_to_wast(node.target), iter=node_to_wast(node.iter), body=node_to_wast(node.body), orelse=node_to_wast(node.orelse), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class While(stmt):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    orelse: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)

    def _to_builtin(self):
        return ast.While(test=wast_to_node(self.test), body=wast_to_node(self.body), orelse=wast_to_node(self.orelse))

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=node_to_wast(node.test), body=node_to_wast(node.body), orelse=node_to_wast(node.orelse))

@attrs.s(kw_only=True)
class If(stmt):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    orelse: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)

    def _to_builtin(self):
        return ast.If(test=wast_to_node(self.test), body=wast_to_node(self.body), orelse=wast_to_node(self.orelse))

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=node_to_wast(node.test), body=node_to_wast(node.body), orelse=node_to_wast(node.orelse))

@attrs.s(kw_only=True)
class With(stmt):
    items: Sequence[withitem] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : withitem)), default=list)
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.With(items=wast_to_node(self.items), body=wast_to_node(self.body), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(items=node_to_wast(node.items), body=node_to_wast(node.body), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class AsyncWith(stmt):
    items: Sequence[withitem] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : withitem)), default=list)
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.AsyncWith(items=wast_to_node(self.items), body=wast_to_node(self.body), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(items=node_to_wast(node.items), body=node_to_wast(node.body), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class Match(stmt):
    subject: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    cases: Sequence[match_case] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : match_case)), default=list)

    def _to_builtin(self):
        return ast.Match(subject=wast_to_node(self.subject), cases=wast_to_node(self.cases))

    @classmethod
    def _from_builtin(cls, node):
        return cls(subject=node_to_wast(node.subject), cases=node_to_wast(node.cases))

@attrs.s(kw_only=True)
class Raise(stmt):
    exc: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    cause: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)

    def _to_builtin(self):
        return ast.Raise(exc=wast_to_node(self.exc), cause=wast_to_node(self.cause))

    @classmethod
    def _from_builtin(cls, node):
        return cls(exc=node_to_wast(node.exc), cause=node_to_wast(node.cause))

@attrs.s(kw_only=True)
class Try(stmt):
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    handlers: Sequence[excepthandler] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : excepthandler)), default=list)
    orelse: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)
    finalbody: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)

    def _to_builtin(self):
        return ast.Try(body=wast_to_node(self.body), handlers=wast_to_node(self.handlers), orelse=wast_to_node(self.orelse), finalbody=wast_to_node(self.finalbody))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=node_to_wast(node.body), handlers=node_to_wast(node.handlers), orelse=node_to_wast(node.orelse), finalbody=node_to_wast(node.finalbody))

@attrs.s(kw_only=True)
class Assert(stmt):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    msg: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)

    def _to_builtin(self):
        return ast.Assert(test=wast_to_node(self.test), msg=wast_to_node(self.msg))

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=node_to_wast(node.test), msg=node_to_wast(node.msg))

@attrs.s(kw_only=True)
class Import(stmt):
    names: Sequence[alias] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : alias)), default=list)

    def _to_builtin(self):
        return ast.Import(names=wast_to_node(self.names))

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node_to_wast(node.names))

@attrs.s(kw_only=True)
class ImportFrom(stmt):
    module: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str), validate_identifier]), default=None)
    names: Sequence[alias] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : alias)), default=list)
    level: Optional[int] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : int)]), default=None)

    def _to_builtin(self):
        return ast.ImportFrom(module=wast_to_node(self.module), names=wast_to_node(self.names), level=wast_to_node(self.level))

    @classmethod
    def _from_builtin(cls, node):
        return cls(module=node_to_wast(node.module), names=node_to_wast(node.names), level=node_to_wast(node.level))

@attrs.s(kw_only=True)
class Global(stmt):
    names: Sequence[str] = attrs.ib(validator=attrs.validators.deep_iterable(attrs.validators.and_(ProxyInstanceOfValidator(lambda : str), validate_identifier)), default=list)

    def _to_builtin(self):
        return ast.Global(names=wast_to_node(self.names))

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node_to_wast(node.names))

@attrs.s(kw_only=True)
class Nonlocal(stmt):
    names: Sequence[str] = attrs.ib(validator=attrs.validators.deep_iterable(attrs.validators.and_(ProxyInstanceOfValidator(lambda : str), validate_identifier)), default=list)

    def _to_builtin(self):
        return ast.Nonlocal(names=wast_to_node(self.names))

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node_to_wast(node.names))

@attrs.s(kw_only=True)
class Expr(stmt):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.Expr(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class Pass(stmt):

    def _to_builtin(self):
        return ast.Pass()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Break(stmt):

    def _to_builtin(self):
        return ast.Break()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Continue(stmt):

    def _to_builtin(self):
        return ast.Continue()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

class expr(Node):
    pass

@attrs.s(kw_only=True)
class BoolOp(expr):
    op: boolop = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : boolop)])
    values: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.BoolOp(op=wast_to_node(self.op), values=wast_to_node(self.values))

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=node_to_wast(node.op), values=node_to_wast(node.values))

@attrs.s(kw_only=True)
class NamedExpr(expr):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.NamedExpr(target=wast_to_node(self.target), value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=node_to_wast(node.target), value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class BinOp(expr):
    left: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    op: operator = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : operator)])
    right: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.BinOp(left=wast_to_node(self.left), op=wast_to_node(self.op), right=wast_to_node(self.right))

    @classmethod
    def _from_builtin(cls, node):
        return cls(left=node_to_wast(node.left), op=node_to_wast(node.op), right=node_to_wast(node.right))

@attrs.s(kw_only=True)
class UnaryOp(expr):
    op: unaryop = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : unaryop)])
    operand: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.UnaryOp(op=wast_to_node(self.op), operand=wast_to_node(self.operand))

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=node_to_wast(node.op), operand=node_to_wast(node.operand))

@attrs.s(kw_only=True)
class Lambda(expr):
    args: arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : arguments)])
    body: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.Lambda(args=wast_to_node(self.args), body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(args=node_to_wast(node.args), body=node_to_wast(node.body))

@attrs.s(kw_only=True)
class IfExp(expr):
    test: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    body: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    orelse: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.IfExp(test=wast_to_node(self.test), body=wast_to_node(self.body), orelse=wast_to_node(self.orelse))

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=node_to_wast(node.test), body=node_to_wast(node.body), orelse=node_to_wast(node.orelse))

@attrs.s(kw_only=True)
class Dict(expr):
    keys: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    values: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.Dict(keys=wast_to_node(self.keys), values=wast_to_node(self.values))

    @classmethod
    def _from_builtin(cls, node):
        return cls(keys=node_to_wast(node.keys), values=node_to_wast(node.values))

@attrs.s(kw_only=True)
class Set(expr):
    elts: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.Set(elts=wast_to_node(self.elts))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=node_to_wast(node.elts))

@attrs.s(kw_only=True)
class ListComp(expr):
    elt: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    generators: Sequence[comprehension] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : comprehension)), default=list)

    def _to_builtin(self):
        return ast.ListComp(elt=wast_to_node(self.elt), generators=wast_to_node(self.generators))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=node_to_wast(node.elt), generators=node_to_wast(node.generators))

@attrs.s(kw_only=True)
class SetComp(expr):
    elt: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    generators: Sequence[comprehension] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : comprehension)), default=list)

    def _to_builtin(self):
        return ast.SetComp(elt=wast_to_node(self.elt), generators=wast_to_node(self.generators))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=node_to_wast(node.elt), generators=node_to_wast(node.generators))

@attrs.s(kw_only=True)
class DictComp(expr):
    key: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    generators: Sequence[comprehension] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : comprehension)), default=list)

    def _to_builtin(self):
        return ast.DictComp(key=wast_to_node(self.key), value=wast_to_node(self.value), generators=wast_to_node(self.generators))

    @classmethod
    def _from_builtin(cls, node):
        return cls(key=node_to_wast(node.key), value=node_to_wast(node.value), generators=node_to_wast(node.generators))

@attrs.s(kw_only=True)
class GeneratorExp(expr):
    elt: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    generators: Sequence[comprehension] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : comprehension)), default=list)

    def _to_builtin(self):
        return ast.GeneratorExp(elt=wast_to_node(self.elt), generators=wast_to_node(self.generators))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=node_to_wast(node.elt), generators=node_to_wast(node.generators))

@attrs.s(kw_only=True)
class Await(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.Await(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class Yield(expr):
    value: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)

    def _to_builtin(self):
        return ast.Yield(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class YieldFrom(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.YieldFrom(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class Compare(expr):
    left: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    ops: Sequence[cmpop] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : cmpop)), default=list)
    comparators: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.Compare(left=wast_to_node(self.left), ops=wast_to_node(self.ops), comparators=wast_to_node(self.comparators))

    @classmethod
    def _from_builtin(cls, node):
        return cls(left=node_to_wast(node.left), ops=node_to_wast(node.ops), comparators=node_to_wast(node.comparators))

@attrs.s(kw_only=True)
class Call(expr):
    func: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    args: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    keywords: Sequence[keyword] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : keyword)), default=list)

    def _to_builtin(self):
        return ast.Call(func=wast_to_node(self.func), args=wast_to_node(self.args), keywords=wast_to_node(self.keywords))

    @classmethod
    def _from_builtin(cls, node):
        return cls(func=node_to_wast(node.func), args=node_to_wast(node.args), keywords=node_to_wast(node.keywords))

@attrs.s(kw_only=True)
class FormattedValue(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    conversion: Optional[int] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : int)]), default=None)
    format_spec: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)

    def _to_builtin(self):
        return ast.FormattedValue(value=wast_to_node(self.value), conversion=wast_to_node(self.conversion), format_spec=wast_to_node(self.format_spec))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value), conversion=node_to_wast(node.conversion), format_spec=node_to_wast(node.format_spec))

@attrs.s(kw_only=True)
class JoinedStr(expr):
    values: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.JoinedStr(values=wast_to_node(self.values))

    @classmethod
    def _from_builtin(cls, node):
        return cls(values=node_to_wast(node.values))

@attrs.s(kw_only=True)
class Constant(expr):
    value: Any = attrs.ib(validator=[])
    kind: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None)

    def _to_builtin(self):
        return ast.Constant(value=wast_to_node(self.value), kind=wast_to_node(self.kind))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value), kind=node_to_wast(node.kind))

@attrs.s(kw_only=True)
class Attribute(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    attr: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str), validate_identifier])
    ctx: Optional[expr_context] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr_context)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.Attribute(value=wast_to_node(self.value), attr=wast_to_node(self.attr), ctx=wast_to_node(self.ctx))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value), attr=node_to_wast(node.attr), ctx=node_to_wast(node.ctx))

@attrs.s(kw_only=True)
class Subscript(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    slice: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    ctx: Optional[expr_context] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr_context)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.Subscript(value=wast_to_node(self.value), slice=wast_to_node(self.slice), ctx=wast_to_node(self.ctx))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value), slice=node_to_wast(node.slice), ctx=node_to_wast(node.ctx))

@attrs.s(kw_only=True)
class Starred(expr):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    ctx: Optional[expr_context] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr_context)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.Starred(value=wast_to_node(self.value), ctx=wast_to_node(self.ctx))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value), ctx=node_to_wast(node.ctx))

@attrs.s(kw_only=True)
class Name(expr):
    id: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str), validate_identifier])
    ctx: Optional[expr_context] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr_context)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.Name(id=wast_to_node(self.id), ctx=wast_to_node(self.ctx))

    @classmethod
    def _from_builtin(cls, node):
        return cls(id=node_to_wast(node.id), ctx=node_to_wast(node.ctx))

@attrs.s(kw_only=True)
class List(expr):
    elts: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    ctx: Optional[expr_context] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr_context)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.List(elts=wast_to_node(self.elts), ctx=wast_to_node(self.ctx))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=node_to_wast(node.elts), ctx=node_to_wast(node.ctx))

@attrs.s(kw_only=True)
class Tuple(expr):
    elts: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    ctx: Optional[expr_context] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr_context)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.Tuple(elts=wast_to_node(self.elts), ctx=wast_to_node(self.ctx))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=node_to_wast(node.elts), ctx=node_to_wast(node.ctx))

@attrs.s(kw_only=True)
class Slice(expr):
    lower: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    upper: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    step: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)

    def _to_builtin(self):
        return ast.Slice(lower=wast_to_node(self.lower), upper=wast_to_node(self.upper), step=wast_to_node(self.step))

    @classmethod
    def _from_builtin(cls, node):
        return cls(lower=node_to_wast(node.lower), upper=node_to_wast(node.upper), step=node_to_wast(node.step))

class expr_context(Node):
    pass

@attrs.s(kw_only=True)
class Load(expr_context):

    def _to_builtin(self):
        return ast.Load()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Store(expr_context):

    def _to_builtin(self):
        return ast.Store()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Del(expr_context):

    def _to_builtin(self):
        return ast.Del()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

class boolop(Node):
    pass

@attrs.s(kw_only=True)
class And(boolop):

    def _to_builtin(self):
        return ast.And()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Or(boolop):

    def _to_builtin(self):
        return ast.Or()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

class operator(Node):
    pass

@attrs.s(kw_only=True)
class Add(operator):

    def _to_builtin(self):
        return ast.Add()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Sub(operator):

    def _to_builtin(self):
        return ast.Sub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Mult(operator):

    def _to_builtin(self):
        return ast.Mult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class MatMult(operator):

    def _to_builtin(self):
        return ast.MatMult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Div(operator):

    def _to_builtin(self):
        return ast.Div()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Mod(operator):

    def _to_builtin(self):
        return ast.Mod()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Pow(operator):

    def _to_builtin(self):
        return ast.Pow()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class LShift(operator):

    def _to_builtin(self):
        return ast.LShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class RShift(operator):

    def _to_builtin(self):
        return ast.RShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class BitOr(operator):

    def _to_builtin(self):
        return ast.BitOr()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class BitXor(operator):

    def _to_builtin(self):
        return ast.BitXor()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class BitAnd(operator):

    def _to_builtin(self):
        return ast.BitAnd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class FloorDiv(operator):

    def _to_builtin(self):
        return ast.FloorDiv()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

class unaryop(Node):
    pass

@attrs.s(kw_only=True)
class Invert(unaryop):

    def _to_builtin(self):
        return ast.Invert()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Not(unaryop):

    def _to_builtin(self):
        return ast.Not()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class UAdd(unaryop):

    def _to_builtin(self):
        return ast.UAdd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class USub(unaryop):

    def _to_builtin(self):
        return ast.USub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

class cmpop(Node):
    pass

@attrs.s(kw_only=True)
class Eq(cmpop):

    def _to_builtin(self):
        return ast.Eq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class NotEq(cmpop):

    def _to_builtin(self):
        return ast.NotEq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Lt(cmpop):

    def _to_builtin(self):
        return ast.Lt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class LtE(cmpop):

    def _to_builtin(self):
        return ast.LtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Gt(cmpop):

    def _to_builtin(self):
        return ast.Gt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class GtE(cmpop):

    def _to_builtin(self):
        return ast.GtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class Is(cmpop):

    def _to_builtin(self):
        return ast.Is()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class IsNot(cmpop):

    def _to_builtin(self):
        return ast.IsNot()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class In(cmpop):

    def _to_builtin(self):
        return ast.In()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class NotIn(cmpop):

    def _to_builtin(self):
        return ast.NotIn()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

@attrs.s(kw_only=True)
class comprehension(Node):
    target: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    iter: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    ifs: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    is_async: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : int)])

    def _to_builtin(self):
        return ast.comprehension(target=wast_to_node(self.target), iter=wast_to_node(self.iter), ifs=wast_to_node(self.ifs), is_async=wast_to_node(self.is_async))

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=node_to_wast(node.target), iter=node_to_wast(node.iter), ifs=node_to_wast(node.ifs), is_async=node_to_wast(node.is_async))

class excepthandler(Node):
    pass

@attrs.s(kw_only=True)
class ExceptHandler(excepthandler):
    type: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    name: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str), validate_identifier]), default=None)
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)

    def _to_builtin(self):
        return ast.ExceptHandler(type=wast_to_node(self.type), name=wast_to_node(self.name), body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(type=node_to_wast(node.type), name=node_to_wast(node.name), body=node_to_wast(node.body))

@attrs.s(kw_only=True)
class arguments(Node):
    posonlyargs: Sequence[arg] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : arg)), default=list)
    args: Sequence[arg] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : arg)), default=list)
    vararg: Optional[arg] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : arg)]), default=None)
    kwonlyargs: Sequence[arg] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : arg)), default=list)
    kw_defaults: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    kwarg: Optional[arg] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : arg)]), default=None)
    defaults: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)

    def _to_builtin(self):
        return ast.arguments(posonlyargs=wast_to_node(self.posonlyargs), args=wast_to_node(self.args), vararg=wast_to_node(self.vararg), kwonlyargs=wast_to_node(self.kwonlyargs), kw_defaults=wast_to_node(self.kw_defaults), kwarg=wast_to_node(self.kwarg), defaults=wast_to_node(self.defaults))

    @classmethod
    def _from_builtin(cls, node):
        return cls(posonlyargs=node_to_wast(node.posonlyargs), args=node_to_wast(node.args), vararg=node_to_wast(node.vararg), kwonlyargs=node_to_wast(node.kwonlyargs), kw_defaults=node_to_wast(node.kw_defaults), kwarg=node_to_wast(node.kwarg), defaults=node_to_wast(node.defaults))

@attrs.s(kw_only=True)
class arg(Node):
    arg: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str), validate_identifier])
    annotation: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    type_comment: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str)]), default=None, repr=False)

    def _to_builtin(self):
        return ast.arg(arg=wast_to_node(self.arg), annotation=wast_to_node(self.annotation), type_comment=wast_to_node(self.type_comment))

    @classmethod
    def _from_builtin(cls, node):
        return cls(arg=node_to_wast(node.arg), annotation=node_to_wast(node.annotation), type_comment=node_to_wast(node.type_comment))

@attrs.s(kw_only=True)
class keyword(Node):
    arg: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str), validate_identifier]), default=None)
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.keyword(arg=wast_to_node(self.arg), value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(arg=node_to_wast(node.arg), value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class alias(Node):
    name: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str), validate_identifier])
    asname: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str), validate_identifier]), default=None)

    def _to_builtin(self):
        return ast.alias(name=wast_to_node(self.name), asname=wast_to_node(self.asname))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name), asname=node_to_wast(node.asname))

@attrs.s(kw_only=True)
class withitem(Node):
    context_expr: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    optional_vars: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)

    def _to_builtin(self):
        return ast.withitem(context_expr=wast_to_node(self.context_expr), optional_vars=wast_to_node(self.optional_vars))

    @classmethod
    def _from_builtin(cls, node):
        return cls(context_expr=node_to_wast(node.context_expr), optional_vars=node_to_wast(node.optional_vars))

@attrs.s(kw_only=True)
class match_case(Node):
    pattern: pattern = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : pattern)])
    guard: Optional[expr] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : expr)]), default=None)
    body: Sequence[stmt] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : stmt)), default=list)

    def _to_builtin(self):
        return ast.match_case(pattern=wast_to_node(self.pattern), guard=wast_to_node(self.guard), body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(pattern=node_to_wast(node.pattern), guard=node_to_wast(node.guard), body=node_to_wast(node.body))

class pattern(Node):
    pass

@attrs.s(kw_only=True)
class MatchValue(pattern):
    value: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])

    def _to_builtin(self):
        return ast.MatchValue(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class MatchSingleton(pattern):
    value: Any = attrs.ib(validator=[])

    def _to_builtin(self):
        return ast.MatchSingleton(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))

@attrs.s(kw_only=True)
class MatchSequence(pattern):
    patterns: Sequence[pattern] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : pattern)), default=list)

    def _to_builtin(self):
        return ast.MatchSequence(patterns=wast_to_node(self.patterns))

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=node_to_wast(node.patterns))

@attrs.s(kw_only=True)
class MatchMapping(pattern):
    keys: Sequence[expr] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : expr)), default=list)
    patterns: Sequence[pattern] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : pattern)), default=list)
    rest: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str), validate_identifier]), default=None)

    def _to_builtin(self):
        return ast.MatchMapping(keys=wast_to_node(self.keys), patterns=wast_to_node(self.patterns), rest=wast_to_node(self.rest))

    @classmethod
    def _from_builtin(cls, node):
        return cls(keys=node_to_wast(node.keys), patterns=node_to_wast(node.patterns), rest=node_to_wast(node.rest))

@attrs.s(kw_only=True)
class MatchClass(pattern):
    cls: expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : expr)])
    patterns: Sequence[pattern] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : pattern)), default=list)
    kwd_attrs: Sequence[str] = attrs.ib(validator=attrs.validators.deep_iterable(attrs.validators.and_(ProxyInstanceOfValidator(lambda : str), validate_identifier)), default=list)
    kwd_patterns: Sequence[pattern] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : pattern)), default=list)

    def _to_builtin(self):
        return ast.MatchClass(cls=wast_to_node(self.cls), patterns=wast_to_node(self.patterns), kwd_attrs=wast_to_node(self.kwd_attrs), kwd_patterns=wast_to_node(self.kwd_patterns))

    @classmethod
    def _from_builtin(cls, node):
        return cls(cls=node_to_wast(node.cls), patterns=node_to_wast(node.patterns), kwd_attrs=node_to_wast(node.kwd_attrs), kwd_patterns=node_to_wast(node.kwd_patterns))

@attrs.s(kw_only=True)
class MatchStar(pattern):
    name: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str), validate_identifier]), default=None)

    def _to_builtin(self):
        return ast.MatchStar(name=wast_to_node(self.name))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name))

@attrs.s(kw_only=True)
class MatchAs(pattern):
    pattern: Optional[pattern] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : pattern)]), default=None)
    name: Optional[str] = attrs.ib(validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda : str), validate_identifier]), default=None)

    def _to_builtin(self):
        return ast.MatchAs(pattern=wast_to_node(self.pattern), name=wast_to_node(self.name))

    @classmethod
    def _from_builtin(cls, node):
        return cls(pattern=node_to_wast(node.pattern), name=node_to_wast(node.name))

@attrs.s(kw_only=True)
class MatchOr(pattern):
    patterns: Sequence[pattern] = attrs.ib(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda : pattern)), default=list)

    def _to_builtin(self):
        return ast.MatchOr(patterns=wast_to_node(self.patterns))

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=node_to_wast(node.patterns))

class type_ignore(Node):
    pass

@attrs.s(kw_only=True)
class TypeIgnore(type_ignore):
    lineno: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : int)])
    tag: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda : str)])

    def _to_builtin(self):
        return ast.TypeIgnore(lineno=wast_to_node(self.lineno), tag=wast_to_node(self.tag))

    @classmethod
    def _from_builtin(cls, node):
        return cls(lineno=node_to_wast(node.lineno), tag=node_to_wast(node.tag))
