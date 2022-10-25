from __future__ import annotations
import ast
import attrs
from typing import Optional, Sequence, Callable
from .validators import (
    convert_identifier,
    DeepIterableConverter,
    ProxyInstanceOfValidator,
)


def unparse(node):
    n = ast.fix_missing_locations(node._to_builtin())
    return ast.unparse(n)


def parse(text):
    node = ast.parse(text)
    return node_to_wast(node)


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


class FreeUnderscore:
    def __getattr__(self, name):
        return BoundUnderscore(Name(id=name))

    def __call__(self, name, *attrs):
        ret = Name(id=name)
        for name in reversed(attrs):
            ret = Attribute(value=ret, attr=name)

        return BoundUnderscore(ret)


_ = FreeUnderscore()


class BoundUnderscore(object):
    def __repr__(self):
        return f"BoundUnderscore({self.__inner__})"

    def __init__(self, inner):
        assert isinstance(inner, expr)
        self.__inner__ = inner

    def __getattr__(self, name):
        return BoundUnderscore(Attribute(value=self.__inner__, attr=name))

    def __call__(self, *args, **kwargs):
        return BoundUnderscore(
            Call(
                func=self.__inner__,
                args=args,
                keywords=[keyword(value=v, arg=k) for k, v in kwargs.items()],
            )
        )

    def __add__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Add(), right=other.__inner__)
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = slice(lower=key.start, upper=key.stop, step=key.step)

        return BoundUnderscore(Subscript(slice=key, value=self.__inner__))

    @property
    def _(self):
        return self.__inner__


class mod(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class Module(mod):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    type_ignores: Sequence[type_ignore] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: type_ignore)
        ),
        factory=list,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Module(
            body=wast_to_node(self.body), type_ignores=wast_to_node(self.type_ignores)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=node_to_wast(node.body), type_ignores=node_to_wast(node.type_ignores)
        )


@attrs.define(hash=True, slots=True, eq=True)
class Interactive(mod):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Interactive(body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=node_to_wast(node.body))


@attrs.define(hash=True, slots=True, eq=True)
class Expression(mod):
    body: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.Expression(body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=node_to_wast(node.body))


@attrs.define(hash=True, slots=True, eq=True)
class FunctionType(mod):
    returns: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    argtypes: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.FunctionType(
            returns=wast_to_node(self.returns), argtypes=wast_to_node(self.argtypes)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            returns=node_to_wast(node.returns), argtypes=node_to_wast(node.argtypes)
        )


class stmt(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class FunctionDef(stmt):
    args: arguments = attrs.field(validator=ProxyInstanceOfValidator(lambda: arguments))
    name: str = attrs.field(converter=convert_identifier)
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    decorator_list: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    returns: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.FunctionDef(
            args=wast_to_node(self.args),
            name=wast_to_node(self.name),
            body=wast_to_node(self.body),
            decorator_list=wast_to_node(self.decorator_list),
            returns=wast_to_node(self.returns),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            args=node_to_wast(node.args),
            name=node_to_wast(node.name),
            body=node_to_wast(node.body),
            decorator_list=node_to_wast(node.decorator_list),
            returns=node_to_wast(node.returns),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class AsyncFunctionDef(stmt):
    args: arguments = attrs.field(validator=ProxyInstanceOfValidator(lambda: arguments))
    name: str = attrs.field(converter=convert_identifier)
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    decorator_list: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    returns: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncFunctionDef(
            args=wast_to_node(self.args),
            name=wast_to_node(self.name),
            body=wast_to_node(self.body),
            decorator_list=wast_to_node(self.decorator_list),
            returns=wast_to_node(self.returns),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            args=node_to_wast(node.args),
            name=node_to_wast(node.name),
            body=node_to_wast(node.body),
            decorator_list=node_to_wast(node.decorator_list),
            returns=node_to_wast(node.returns),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class ClassDef(stmt):
    name: str = attrs.field(converter=convert_identifier)
    bases: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    decorator_list: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    keywords: Sequence[keyword] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: keyword)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.ClassDef(
            name=wast_to_node(self.name),
            bases=wast_to_node(self.bases),
            body=wast_to_node(self.body),
            decorator_list=wast_to_node(self.decorator_list),
            keywords=wast_to_node(self.keywords),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            name=node_to_wast(node.name),
            bases=node_to_wast(node.bases),
            body=node_to_wast(node.body),
            decorator_list=node_to_wast(node.decorator_list),
            keywords=node_to_wast(node.keywords),
        )


@attrs.define(hash=True, slots=True, eq=True)
class Return(stmt):
    value: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.Return(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class Delete(stmt):
    targets: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Delete(targets=wast_to_node(self.targets))

    @classmethod
    def _from_builtin(cls, node):
        return cls(targets=node_to_wast(node.targets))


@attrs.define(hash=True, slots=True, eq=True)
class Assign(stmt):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    targets: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Assign(
            value=wast_to_node(self.value),
            targets=wast_to_node(self.targets),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            value=node_to_wast(node.value),
            targets=node_to_wast(node.targets),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class AugAssign(stmt):
    op: operator = attrs.field(validator=ProxyInstanceOfValidator(lambda: operator))
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.AugAssign(
            op=wast_to_node(self.op),
            target=wast_to_node(self.target),
            value=wast_to_node(self.value),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            op=node_to_wast(node.op),
            target=node_to_wast(node.target),
            value=node_to_wast(node.value),
        )


@attrs.define(hash=True, slots=True, eq=True)
class AnnAssign(stmt):
    annotation: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    simple: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    value: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.AnnAssign(
            annotation=wast_to_node(self.annotation),
            simple=wast_to_node(self.simple),
            target=wast_to_node(self.target),
            value=wast_to_node(self.value),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            annotation=node_to_wast(node.annotation),
            simple=node_to_wast(node.simple),
            target=node_to_wast(node.target),
            value=node_to_wast(node.value),
        )


@attrs.define(hash=True, slots=True, eq=True)
class For(stmt):
    iter: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.For(
            iter=wast_to_node(self.iter),
            target=wast_to_node(self.target),
            body=wast_to_node(self.body),
            orelse=wast_to_node(self.orelse),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            iter=node_to_wast(node.iter),
            target=node_to_wast(node.target),
            body=node_to_wast(node.body),
            orelse=node_to_wast(node.orelse),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class AsyncFor(stmt):
    iter: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncFor(
            iter=wast_to_node(self.iter),
            target=wast_to_node(self.target),
            body=wast_to_node(self.body),
            orelse=wast_to_node(self.orelse),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            iter=node_to_wast(node.iter),
            target=node_to_wast(node.target),
            body=node_to_wast(node.body),
            orelse=node_to_wast(node.orelse),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class While(stmt):
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.While(
            test=wast_to_node(self.test),
            body=wast_to_node(self.body),
            orelse=wast_to_node(self.orelse),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            test=node_to_wast(node.test),
            body=node_to_wast(node.body),
            orelse=node_to_wast(node.orelse),
        )


@attrs.define(hash=True, slots=True, eq=True)
class If(stmt):
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.If(
            test=wast_to_node(self.test),
            body=wast_to_node(self.body),
            orelse=wast_to_node(self.orelse),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            test=node_to_wast(node.test),
            body=node_to_wast(node.body),
            orelse=node_to_wast(node.orelse),
        )


@attrs.define(hash=True, slots=True, eq=True)
class With(stmt):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    items: Sequence[withitem] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: withitem)
        ),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.With(
            body=wast_to_node(self.body),
            items=wast_to_node(self.items),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=node_to_wast(node.body),
            items=node_to_wast(node.items),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class AsyncWith(stmt):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    items: Sequence[withitem] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: withitem)
        ),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncWith(
            body=wast_to_node(self.body),
            items=wast_to_node(self.items),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=node_to_wast(node.body),
            items=node_to_wast(node.items),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class Match(stmt):
    subject: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    cases: Sequence[match_case] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: match_case)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Match(
            subject=wast_to_node(self.subject), cases=wast_to_node(self.cases)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(subject=node_to_wast(node.subject), cases=node_to_wast(node.cases))


@attrs.define(hash=True, slots=True, eq=True)
class Raise(stmt):
    cause: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )
    exc: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.Raise(cause=wast_to_node(self.cause), exc=wast_to_node(self.exc))

    @classmethod
    def _from_builtin(cls, node):
        return cls(cause=node_to_wast(node.cause), exc=node_to_wast(node.exc))


@attrs.define(hash=True, slots=True, eq=True)
class Try(stmt):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    finalbody: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    handlers: Sequence[excepthandler] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: excepthandler)
        ),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Try(
            body=wast_to_node(self.body),
            finalbody=wast_to_node(self.finalbody),
            handlers=wast_to_node(self.handlers),
            orelse=wast_to_node(self.orelse),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=node_to_wast(node.body),
            finalbody=node_to_wast(node.finalbody),
            handlers=node_to_wast(node.handlers),
            orelse=node_to_wast(node.orelse),
        )


@attrs.define(hash=True, slots=True, eq=True)
class Assert(stmt):
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    msg: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.Assert(test=wast_to_node(self.test), msg=wast_to_node(self.msg))

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=node_to_wast(node.test), msg=node_to_wast(node.msg))


@attrs.define(hash=True, slots=True, eq=True)
class Import(stmt):
    names: Sequence[alias] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: alias)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Import(names=wast_to_node(self.names))

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node_to_wast(node.names))


@attrs.define(hash=True, slots=True, eq=True)
class ImportFrom(stmt):
    level: Optional[int] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: int)),
        default=None,
    )
    module: Optional[str] = attrs.field(default=None, converter=convert_identifier)
    names: Sequence[alias] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: alias)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.ImportFrom(
            level=wast_to_node(self.level),
            module=wast_to_node(self.module),
            names=wast_to_node(self.names),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            level=node_to_wast(node.level),
            module=node_to_wast(node.module),
            names=node_to_wast(node.names),
        )


@attrs.define(hash=True, slots=True, eq=True)
class Global(stmt):
    names: Sequence[str] = attrs.field(
        factory=list, converter=DeepIterableConverter(convert_identifier)
    )

    def _to_builtin(self):
        return ast.Global(names=wast_to_node(self.names))

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node_to_wast(node.names))


@attrs.define(hash=True, slots=True, eq=True)
class Nonlocal(stmt):
    names: Sequence[str] = attrs.field(
        factory=list, converter=DeepIterableConverter(convert_identifier)
    )

    def _to_builtin(self):
        return ast.Nonlocal(names=wast_to_node(self.names))

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node_to_wast(node.names))


@attrs.define(hash=True, slots=True, eq=True)
class Expr(stmt):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.Expr(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class Pass(stmt):
    def _to_builtin(self):
        return ast.Pass()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Break(stmt):
    def _to_builtin(self):
        return ast.Break()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Continue(stmt):
    def _to_builtin(self):
        return ast.Continue()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


class expr(Node):
    def __call__(self, *attrs):
        ret = self
        for name in reversed(attrs):
            ret = Attribute(value=ret, attr=name)
        return BoundUnderscore(ret)


@attrs.define(hash=True, slots=True, eq=True)
class BoolOp(expr):
    op: boolop = attrs.field(validator=ProxyInstanceOfValidator(lambda: boolop))
    values: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.BoolOp(op=wast_to_node(self.op), values=wast_to_node(self.values))

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=node_to_wast(node.op), values=node_to_wast(node.values))


@attrs.define(hash=True, slots=True, eq=True)
class NamedExpr(expr):
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.NamedExpr(
            target=wast_to_node(self.target), value=wast_to_node(self.value)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=node_to_wast(node.target), value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class BinOp(expr):
    left: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    op: operator = attrs.field(validator=ProxyInstanceOfValidator(lambda: operator))
    right: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.BinOp(
            left=wast_to_node(self.left),
            op=wast_to_node(self.op),
            right=wast_to_node(self.right),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            left=node_to_wast(node.left),
            op=node_to_wast(node.op),
            right=node_to_wast(node.right),
        )


@attrs.define(hash=True, slots=True, eq=True)
class UnaryOp(expr):
    op: unaryop = attrs.field(validator=ProxyInstanceOfValidator(lambda: unaryop))
    operand: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.UnaryOp(op=wast_to_node(self.op), operand=wast_to_node(self.operand))

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=node_to_wast(node.op), operand=node_to_wast(node.operand))


@attrs.define(hash=True, slots=True, eq=True)
class Lambda(expr):
    args: arguments = attrs.field(validator=ProxyInstanceOfValidator(lambda: arguments))
    body: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.Lambda(args=wast_to_node(self.args), body=wast_to_node(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(args=node_to_wast(node.args), body=node_to_wast(node.body))


@attrs.define(hash=True, slots=True, eq=True)
class IfExp(expr):
    body: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    orelse: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.IfExp(
            body=wast_to_node(self.body),
            orelse=wast_to_node(self.orelse),
            test=wast_to_node(self.test),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=node_to_wast(node.body),
            orelse=node_to_wast(node.orelse),
            test=node_to_wast(node.test),
        )


@attrs.define(hash=True, slots=True, eq=True)
class Dict(expr):
    keys: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    values: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Dict(keys=wast_to_node(self.keys), values=wast_to_node(self.values))

    @classmethod
    def _from_builtin(cls, node):
        return cls(keys=node_to_wast(node.keys), values=node_to_wast(node.values))


@attrs.define(hash=True, slots=True, eq=True)
class Set(expr):
    elts: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Set(elts=wast_to_node(self.elts))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=node_to_wast(node.elts))


@attrs.define(hash=True, slots=True, eq=True)
class ListComp(expr):
    elt: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.ListComp(
            elt=wast_to_node(self.elt), generators=wast_to_node(self.generators)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=node_to_wast(node.elt), generators=node_to_wast(node.generators))


@attrs.define(hash=True, slots=True, eq=True)
class SetComp(expr):
    elt: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.SetComp(
            elt=wast_to_node(self.elt), generators=wast_to_node(self.generators)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=node_to_wast(node.elt), generators=node_to_wast(node.generators))


@attrs.define(hash=True, slots=True, eq=True)
class DictComp(expr):
    key: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.DictComp(
            key=wast_to_node(self.key),
            value=wast_to_node(self.value),
            generators=wast_to_node(self.generators),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            key=node_to_wast(node.key),
            value=node_to_wast(node.value),
            generators=node_to_wast(node.generators),
        )


@attrs.define(hash=True, slots=True, eq=True)
class GeneratorExp(expr):
    elt: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.GeneratorExp(
            elt=wast_to_node(self.elt), generators=wast_to_node(self.generators)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=node_to_wast(node.elt), generators=node_to_wast(node.generators))


@attrs.define(hash=True, slots=True, eq=True)
class Await(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.Await(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class Yield(expr):
    value: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.Yield(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class YieldFrom(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.YieldFrom(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class Compare(expr):
    left: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    comparators: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    ops: Sequence[cmpop] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: cmpop)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Compare(
            left=wast_to_node(self.left),
            comparators=wast_to_node(self.comparators),
            ops=wast_to_node(self.ops),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            left=node_to_wast(node.left),
            comparators=node_to_wast(node.comparators),
            ops=node_to_wast(node.ops),
        )


@attrs.define(hash=True, slots=True, eq=True)
class Call(expr):
    func: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    args: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    keywords: Sequence[keyword] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: keyword)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Call(
            func=wast_to_node(self.func),
            args=wast_to_node(self.args),
            keywords=wast_to_node(self.keywords),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            func=node_to_wast(node.func),
            args=node_to_wast(node.args),
            keywords=node_to_wast(node.keywords),
        )


@attrs.define(hash=True, slots=True, eq=True)
class FormattedValue(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    conversion: Optional[int] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: int)),
        default=None,
    )
    format_spec: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.FormattedValue(
            value=wast_to_node(self.value),
            conversion=wast_to_node(self.conversion),
            format_spec=wast_to_node(self.format_spec),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            value=node_to_wast(node.value),
            conversion=node_to_wast(node.conversion),
            format_spec=node_to_wast(node.format_spec),
        )


@attrs.define(hash=True, slots=True, eq=True)
class JoinedStr(expr):
    values: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.JoinedStr(values=wast_to_node(self.values))

    @classmethod
    def _from_builtin(cls, node):
        return cls(values=node_to_wast(node.values))


@attrs.define(hash=True, slots=True, eq=True)
class Constant(expr):
    value: Any = attrs.field()
    kind: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
    )

    def _to_builtin(self):
        return ast.Constant(
            value=wast_to_node(self.value), kind=wast_to_node(self.kind)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value), kind=node_to_wast(node.kind))


@attrs.define(hash=True, slots=True, eq=True)
class Attribute(expr):
    attr: str = attrs.field(converter=convert_identifier)
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.Attribute(
            attr=wast_to_node(self.attr), value=wast_to_node(self.value)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(attr=node_to_wast(node.attr), value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class Subscript(expr):
    slice: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.Subscript(
            slice=wast_to_node(self.slice), value=wast_to_node(self.value)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(slice=node_to_wast(node.slice), value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class Starred(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.Starred(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class Name(expr):
    id: str = attrs.field(converter=convert_identifier)

    def _to_builtin(self):
        return ast.Name(id=wast_to_node(self.id))

    @classmethod
    def _from_builtin(cls, node):
        return cls(id=node_to_wast(node.id))


@attrs.define(hash=True, slots=True, eq=True)
class List(expr):
    elts: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.List(elts=wast_to_node(self.elts))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=node_to_wast(node.elts))


@attrs.define(hash=True, slots=True, eq=True)
class Tuple(expr):
    elts: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Tuple(elts=wast_to_node(self.elts))

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=node_to_wast(node.elts))


@attrs.define(hash=True, slots=True, eq=True)
class Slice(expr):
    lower: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )
    step: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )
    upper: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.Slice(
            lower=wast_to_node(self.lower),
            step=wast_to_node(self.step),
            upper=wast_to_node(self.upper),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            lower=node_to_wast(node.lower),
            step=node_to_wast(node.step),
            upper=node_to_wast(node.upper),
        )


class expr_context(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class Load(expr_context):
    def _to_builtin(self):
        return ast.Load()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Store(expr_context):
    def _to_builtin(self):
        return ast.Store()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Del(expr_context):
    def _to_builtin(self):
        return ast.Del()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


class boolop(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class And(boolop):
    def _to_builtin(self):
        return ast.And()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Or(boolop):
    def _to_builtin(self):
        return ast.Or()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


class operator(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class Add(operator):
    def _to_builtin(self):
        return ast.Add()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Sub(operator):
    def _to_builtin(self):
        return ast.Sub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Mult(operator):
    def _to_builtin(self):
        return ast.Mult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class MatMult(operator):
    def _to_builtin(self):
        return ast.MatMult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Div(operator):
    def _to_builtin(self):
        return ast.Div()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Mod(operator):
    def _to_builtin(self):
        return ast.Mod()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Pow(operator):
    def _to_builtin(self):
        return ast.Pow()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class LShift(operator):
    def _to_builtin(self):
        return ast.LShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class RShift(operator):
    def _to_builtin(self):
        return ast.RShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class BitOr(operator):
    def _to_builtin(self):
        return ast.BitOr()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class BitXor(operator):
    def _to_builtin(self):
        return ast.BitXor()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class BitAnd(operator):
    def _to_builtin(self):
        return ast.BitAnd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class FloorDiv(operator):
    def _to_builtin(self):
        return ast.FloorDiv()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


class unaryop(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class Invert(unaryop):
    def _to_builtin(self):
        return ast.Invert()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Not(unaryop):
    def _to_builtin(self):
        return ast.Not()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class UAdd(unaryop):
    def _to_builtin(self):
        return ast.UAdd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class USub(unaryop):
    def _to_builtin(self):
        return ast.USub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


class cmpop(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class Eq(cmpop):
    def _to_builtin(self):
        return ast.Eq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class NotEq(cmpop):
    def _to_builtin(self):
        return ast.NotEq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Lt(cmpop):
    def _to_builtin(self):
        return ast.Lt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class LtE(cmpop):
    def _to_builtin(self):
        return ast.LtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Gt(cmpop):
    def _to_builtin(self):
        return ast.Gt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class GtE(cmpop):
    def _to_builtin(self):
        return ast.GtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class Is(cmpop):
    def _to_builtin(self):
        return ast.Is()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class IsNot(cmpop):
    def _to_builtin(self):
        return ast.IsNot()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class In(cmpop):
    def _to_builtin(self):
        return ast.In()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class NotIn(cmpop):
    def _to_builtin(self):
        return ast.NotIn()

    @classmethod
    def _from_builtin(cls, node):
        return cls()


@attrs.define(hash=True, slots=True, eq=True)
class comprehension(Node):
    is_async: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    iter: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    ifs: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.comprehension(
            is_async=wast_to_node(self.is_async),
            iter=wast_to_node(self.iter),
            target=wast_to_node(self.target),
            ifs=wast_to_node(self.ifs),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            is_async=node_to_wast(node.is_async),
            iter=node_to_wast(node.iter),
            target=node_to_wast(node.target),
            ifs=node_to_wast(node.ifs),
        )


class excepthandler(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class ExceptHandler(excepthandler):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    name: Optional[str] = attrs.field(default=None, converter=convert_identifier)
    type: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.ExceptHandler(
            body=wast_to_node(self.body),
            name=wast_to_node(self.name),
            type=wast_to_node(self.type),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=node_to_wast(node.body),
            name=node_to_wast(node.name),
            type=node_to_wast(node.type),
        )


@attrs.define(hash=True, slots=True, eq=True)
class arguments(Node):
    args: Sequence[arg] = attrs.field(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        factory=list,
    )
    defaults: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    kw_defaults: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    kwarg: Optional[arg] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: arg)),
        default=None,
    )
    kwonlyargs: Sequence[arg] = attrs.field(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        factory=list,
    )
    posonlyargs: Sequence[arg] = attrs.field(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        factory=list,
    )
    vararg: Optional[arg] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: arg)),
        default=None,
    )

    def _to_builtin(self):
        return ast.arguments(
            args=wast_to_node(self.args),
            defaults=wast_to_node(self.defaults),
            kw_defaults=wast_to_node(self.kw_defaults),
            kwarg=wast_to_node(self.kwarg),
            kwonlyargs=wast_to_node(self.kwonlyargs),
            posonlyargs=wast_to_node(self.posonlyargs),
            vararg=wast_to_node(self.vararg),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            args=node_to_wast(node.args),
            defaults=node_to_wast(node.defaults),
            kw_defaults=node_to_wast(node.kw_defaults),
            kwarg=node_to_wast(node.kwarg),
            kwonlyargs=node_to_wast(node.kwonlyargs),
            posonlyargs=node_to_wast(node.posonlyargs),
            vararg=node_to_wast(node.vararg),
        )


@attrs.define(hash=True, slots=True, eq=True)
class arg(Node):
    arg: str = attrs.field(converter=convert_identifier)
    annotation: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.arg(
            arg=wast_to_node(self.arg),
            annotation=wast_to_node(self.annotation),
            type_comment=wast_to_node(self.type_comment),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            arg=node_to_wast(node.arg),
            annotation=node_to_wast(node.annotation),
            type_comment=node_to_wast(node.type_comment),
        )


@attrs.define(hash=True, slots=True, eq=True)
class keyword(Node):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    arg: Optional[str] = attrs.field(default=None, converter=convert_identifier)

    def _to_builtin(self):
        return ast.keyword(value=wast_to_node(self.value), arg=wast_to_node(self.arg))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value), arg=node_to_wast(node.arg))


@attrs.define(hash=True, slots=True, eq=True)
class alias(Node):
    name: str = attrs.field(converter=convert_identifier)
    asname: Optional[str] = attrs.field(default=None, converter=convert_identifier)

    def _to_builtin(self):
        return ast.alias(name=wast_to_node(self.name), asname=wast_to_node(self.asname))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name), asname=node_to_wast(node.asname))


@attrs.define(hash=True, slots=True, eq=True)
class withitem(Node):
    context_expr: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    optional_vars: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.withitem(
            context_expr=wast_to_node(self.context_expr),
            optional_vars=wast_to_node(self.optional_vars),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            context_expr=node_to_wast(node.context_expr),
            optional_vars=node_to_wast(node.optional_vars),
        )


@attrs.define(hash=True, slots=True, eq=True)
class match_case(Node):
    pattern: pattern = attrs.field(validator=ProxyInstanceOfValidator(lambda: pattern))
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        factory=list,
    )
    guard: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        default=None,
    )

    def _to_builtin(self):
        return ast.match_case(
            pattern=wast_to_node(self.pattern),
            body=wast_to_node(self.body),
            guard=wast_to_node(self.guard),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            pattern=node_to_wast(node.pattern),
            body=node_to_wast(node.body),
            guard=node_to_wast(node.guard),
        )


class pattern(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class MatchValue(pattern):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))

    def _to_builtin(self):
        return ast.MatchValue(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class MatchSingleton(pattern):
    value: Any = attrs.field()

    def _to_builtin(self):
        return ast.MatchSingleton(value=wast_to_node(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node_to_wast(node.value))


@attrs.define(hash=True, slots=True, eq=True)
class MatchSequence(pattern):
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.MatchSequence(patterns=wast_to_node(self.patterns))

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=node_to_wast(node.patterns))


@attrs.define(hash=True, slots=True, eq=True)
class MatchMapping(pattern):
    keys: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        factory=list,
    )
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        factory=list,
    )
    rest: Optional[str] = attrs.field(default=None, converter=convert_identifier)

    def _to_builtin(self):
        return ast.MatchMapping(
            keys=wast_to_node(self.keys),
            patterns=wast_to_node(self.patterns),
            rest=wast_to_node(self.rest),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            keys=node_to_wast(node.keys),
            patterns=node_to_wast(node.patterns),
            rest=node_to_wast(node.rest),
        )


@attrs.define(hash=True, slots=True, eq=True)
class MatchClass(pattern):
    cls: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr))
    kwd_attrs: Sequence[str] = attrs.field(
        factory=list, converter=DeepIterableConverter(convert_identifier)
    )
    kwd_patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        factory=list,
    )
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.MatchClass(
            cls=wast_to_node(self.cls),
            kwd_attrs=wast_to_node(self.kwd_attrs),
            kwd_patterns=wast_to_node(self.kwd_patterns),
            patterns=wast_to_node(self.patterns),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            cls=node_to_wast(node.cls),
            kwd_attrs=node_to_wast(node.kwd_attrs),
            kwd_patterns=node_to_wast(node.kwd_patterns),
            patterns=node_to_wast(node.patterns),
        )


@attrs.define(hash=True, slots=True, eq=True)
class MatchStar(pattern):
    name: Optional[str] = attrs.field(default=None, converter=convert_identifier)

    def _to_builtin(self):
        return ast.MatchStar(name=wast_to_node(self.name))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name))


@attrs.define(hash=True, slots=True, eq=True)
class MatchAs(pattern):
    name: Optional[str] = attrs.field(default=None, converter=convert_identifier)
    pattern: Optional[pattern] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: pattern)),
        default=None,
    )

    def _to_builtin(self):
        return ast.MatchAs(
            name=wast_to_node(self.name), pattern=wast_to_node(self.pattern)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node_to_wast(node.name), pattern=node_to_wast(node.pattern))


@attrs.define(hash=True, slots=True, eq=True)
class MatchOr(pattern):
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        factory=list,
    )

    def _to_builtin(self):
        return ast.MatchOr(patterns=wast_to_node(self.patterns))

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=node_to_wast(node.patterns))


class type_ignore(Node):
    pass


@attrs.define(hash=True, slots=True, eq=True)
class TypeIgnore(type_ignore):
    lineno: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    tag: str = attrs.field(validator=ProxyInstanceOfValidator(lambda: str))

    def _to_builtin(self):
        return ast.TypeIgnore(
            lineno=wast_to_node(self.lineno), tag=wast_to_node(self.tag)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(lineno=node_to_wast(node.lineno), tag=node_to_wast(node.tag))
