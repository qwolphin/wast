from __future__ import annotations
import ast
import attrs
from typing import Optional, Sequence, Callable
from .validators import (
    convert_identifier,
    unwrap_underscore,
    DeepIterableConverter,
    ProxyInstanceOfValidator,
)


def unparse(node: Node) -> str:
    tree = to_builtin(node)
    tree = ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def parse(text: str) -> Node:
    tree = ast.parse(text)
    return from_builtin(tree)


class Node:
    pass


def to_builtin(node: Node):
    assert isinstance(node, Node)
    return node._to_builtin()


def from_builtin(node: ast.AST) -> Node:
    assert isinstance(node, ast.AST)
    t = node.__class__.__name__
    return NODES[t]._from_builtin(node)


@attrs.define
class TransformerContext:
    parents: Sequence[Node] = attrs.field(factory=list)


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

    def __and__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=And(), right=other.__inner__)
        )

    def __floordiv__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=FloorDiv(), right=other.__inner__)
        )

    def __mod__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Mod(), right=other.__inner__)
        )

    def __lshift__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=LShift(), right=other.__inner__)
        )

    def __rshift__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=RShift(), right=other.__inner__)
        )

    def __matmul__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=MatMult(), right=other.__inner__)
        )

    def __sub__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Sub(), right=other.__inner__)
        )

    def __pow__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Mod(), right=other.__inner__)
        )

    def __div__(self, other):
        return BoundUnderscore(
            BinOp(left=self.__inner__, op=Div(), right=other.__inner__)
        )

    def __lt__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Lt()])
        )

    def __gt__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Gt()])
        )

    def __le__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Le()])
        )

    def __ge__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Ge()])
        )

    def __lt__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Lt()])
        )

    def __eq__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Eq()])
        )

    def __ne__(self, other):
        return BoundUnderscore(
            Compare(left=self.__inner__, comparators=[other.__inner__], ops=[NotEq()])
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


@attrs.define()
class Module(mod):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    type_ignores: Sequence[type_ignore] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: type_ignore)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Module(
            body=[to_builtin(x) for x in self.body],
            type_ignores=[to_builtin(x) for x in self.type_ignores],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=[from_builtin(x) for x in node.body],
            type_ignores=[from_builtin(x) for x in node.type_ignores],
        )

    def _transform(self, node_transformer, context):
        return Module(
            body=[node_transformer(x, context) for x in self.body],
            type_ignores=[node_transformer(x, context) for x in self.type_ignores],
        )

    def _nodes_iter(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.type_ignores:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Interactive(mod):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Interactive(body=[to_builtin(x) for x in self.body])

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=[from_builtin(x) for x in node.body])

    def _transform(self, node_transformer, context):
        return Interactive(body=[node_transformer(x, context) for x in self.body])

    def _nodes_iter(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Expression(mod):
    body: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.Expression(body=to_builtin(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=from_builtin(node.body))

    def _transform(self, node_transformer, context):
        return Expression(body=node_transformer(self.body, context))

    def _nodes_iter(self):
        yield self
        yield from self.body._nodes_iter()


@attrs.define()
class FunctionType(mod):
    returns: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    argtypes: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.FunctionType(
            returns=to_builtin(self.returns),
            argtypes=[to_builtin(x) for x in self.argtypes],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            returns=from_builtin(node.returns),
            argtypes=[from_builtin(x) for x in node.argtypes],
        )

    def _transform(self, node_transformer, context):
        return FunctionType(
            returns=node_transformer(self.returns, context),
            argtypes=[node_transformer(x, context) for x in self.argtypes],
        )

    def _nodes_iter(self):
        yield self
        yield from self.returns._nodes_iter()
        for x in self.argtypes:
            if x is not None:
                yield from x._nodes_iter()


class stmt(Node):
    pass


@attrs.define()
class FunctionDef(stmt):
    args: arguments = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: arguments),
        converter=unwrap_underscore,
    )
    name: str = attrs.field(converter=convert_identifier)
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    decorator_list: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    returns: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.FunctionDef(
            args=to_builtin(self.args),
            name=self.name,
            body=[to_builtin(x) for x in self.body],
            decorator_list=[to_builtin(x) for x in self.decorator_list],
            returns=None if self.returns is None else to_builtin(self.returns),
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            args=from_builtin(node.args),
            name=node.name,
            body=[from_builtin(x) for x in node.body],
            decorator_list=[from_builtin(x) for x in node.decorator_list],
            returns=None if node.returns is None else from_builtin(node.returns),
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return FunctionDef(
            args=node_transformer(self.args, context),
            name=self.name,
            body=[node_transformer(x, context) for x in self.body],
            decorator_list=[node_transformer(x, context) for x in self.decorator_list],
            returns=None
            if self.returns is None
            else node_transformer(self.returns, context),
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        yield from self.args._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.decorator_list:
            if x is not None:
                yield from x._nodes_iter()
        if self.returns is not None:
            yield from self.returns._nodes_iter()


@attrs.define()
class AsyncFunctionDef(stmt):
    args: arguments = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: arguments),
        converter=unwrap_underscore,
    )
    name: str = attrs.field(converter=convert_identifier)
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    decorator_list: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    returns: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncFunctionDef(
            args=to_builtin(self.args),
            name=self.name,
            body=[to_builtin(x) for x in self.body],
            decorator_list=[to_builtin(x) for x in self.decorator_list],
            returns=None if self.returns is None else to_builtin(self.returns),
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            args=from_builtin(node.args),
            name=node.name,
            body=[from_builtin(x) for x in node.body],
            decorator_list=[from_builtin(x) for x in node.decorator_list],
            returns=None if node.returns is None else from_builtin(node.returns),
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return AsyncFunctionDef(
            args=node_transformer(self.args, context),
            name=self.name,
            body=[node_transformer(x, context) for x in self.body],
            decorator_list=[node_transformer(x, context) for x in self.decorator_list],
            returns=None
            if self.returns is None
            else node_transformer(self.returns, context),
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        yield from self.args._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.decorator_list:
            if x is not None:
                yield from x._nodes_iter()
        if self.returns is not None:
            yield from self.returns._nodes_iter()


@attrs.define()
class ClassDef(stmt):
    name: str = attrs.field(converter=convert_identifier)
    bases: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    decorator_list: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    keywords: Sequence[keyword] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: keyword)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.ClassDef(
            name=self.name,
            bases=[to_builtin(x) for x in self.bases],
            body=[to_builtin(x) for x in self.body],
            decorator_list=[to_builtin(x) for x in self.decorator_list],
            keywords=[to_builtin(x) for x in self.keywords],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            name=node.name,
            bases=[from_builtin(x) for x in node.bases],
            body=[from_builtin(x) for x in node.body],
            decorator_list=[from_builtin(x) for x in node.decorator_list],
            keywords=[from_builtin(x) for x in node.keywords],
        )

    def _transform(self, node_transformer, context):
        return ClassDef(
            name=self.name,
            bases=[node_transformer(x, context) for x in self.bases],
            body=[node_transformer(x, context) for x in self.body],
            decorator_list=[node_transformer(x, context) for x in self.decorator_list],
            keywords=[node_transformer(x, context) for x in self.keywords],
        )

    def _nodes_iter(self):
        yield self
        for x in self.bases:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.decorator_list:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.keywords:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Return(stmt):
    value: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.Return(value=None if self.value is None else to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=None if node.value is None else from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return Return(
            value=None if self.value is None else node_transformer(self.value, context)
        )

    def _nodes_iter(self):
        yield self
        if self.value is not None:
            yield from self.value._nodes_iter()


@attrs.define()
class Delete(stmt):
    targets: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Delete(targets=[to_builtin(x) for x in self.targets])

    @classmethod
    def _from_builtin(cls, node):
        return cls(targets=[from_builtin(x) for x in node.targets])

    def _transform(self, node_transformer, context):
        return Delete(targets=[node_transformer(x, context) for x in self.targets])

    def _nodes_iter(self):
        yield self
        for x in self.targets:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Assign(stmt):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    targets: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.Assign(
            value=to_builtin(self.value),
            targets=[to_builtin(x) for x in self.targets],
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            value=from_builtin(node.value),
            targets=[from_builtin(x) for x in node.targets],
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return Assign(
            value=node_transformer(self.value, context),
            targets=[node_transformer(x, context) for x in self.targets],
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()
        for x in self.targets:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class AugAssign(stmt):
    op: operator = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: operator),
        converter=unwrap_underscore,
    )
    target: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.AugAssign(
            op=to_builtin(self.op),
            target=to_builtin(self.target),
            value=to_builtin(self.value),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            op=from_builtin(node.op),
            target=from_builtin(node.target),
            value=from_builtin(node.value),
        )

    def _transform(self, node_transformer, context):
        return AugAssign(
            op=node_transformer(self.op, context),
            target=node_transformer(self.target, context),
            value=node_transformer(self.value, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.op._nodes_iter()
        yield from self.target._nodes_iter()
        yield from self.value._nodes_iter()


@attrs.define()
class AnnAssign(stmt):
    annotation: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    simple: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    target: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    value: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.AnnAssign(
            annotation=to_builtin(self.annotation),
            simple=self.simple,
            target=to_builtin(self.target),
            value=None if self.value is None else to_builtin(self.value),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            annotation=from_builtin(node.annotation),
            simple=node.simple,
            target=from_builtin(node.target),
            value=None if node.value is None else from_builtin(node.value),
        )

    def _transform(self, node_transformer, context):
        return AnnAssign(
            annotation=node_transformer(self.annotation, context),
            simple=self.simple,
            target=node_transformer(self.target, context),
            value=None if self.value is None else node_transformer(self.value, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.annotation._nodes_iter()
        yield from self.target._nodes_iter()
        if self.value is not None:
            yield from self.value._nodes_iter()


@attrs.define()
class For(stmt):
    iter: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    target: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.For(
            iter=to_builtin(self.iter),
            target=to_builtin(self.target),
            body=[to_builtin(x) for x in self.body],
            orelse=[to_builtin(x) for x in self.orelse],
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            iter=from_builtin(node.iter),
            target=from_builtin(node.target),
            body=[from_builtin(x) for x in node.body],
            orelse=[from_builtin(x) for x in node.orelse],
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return For(
            iter=node_transformer(self.iter, context),
            target=node_transformer(self.target, context),
            body=[node_transformer(x, context) for x in self.body],
            orelse=[node_transformer(x, context) for x in self.orelse],
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        yield from self.iter._nodes_iter()
        yield from self.target._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.orelse:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class AsyncFor(stmt):
    iter: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    target: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncFor(
            iter=to_builtin(self.iter),
            target=to_builtin(self.target),
            body=[to_builtin(x) for x in self.body],
            orelse=[to_builtin(x) for x in self.orelse],
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            iter=from_builtin(node.iter),
            target=from_builtin(node.target),
            body=[from_builtin(x) for x in node.body],
            orelse=[from_builtin(x) for x in node.orelse],
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return AsyncFor(
            iter=node_transformer(self.iter, context),
            target=node_transformer(self.target, context),
            body=[node_transformer(x, context) for x in self.body],
            orelse=[node_transformer(x, context) for x in self.orelse],
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        yield from self.iter._nodes_iter()
        yield from self.target._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.orelse:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class While(stmt):
    test: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.While(
            test=to_builtin(self.test),
            body=[to_builtin(x) for x in self.body],
            orelse=[to_builtin(x) for x in self.orelse],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            test=from_builtin(node.test),
            body=[from_builtin(x) for x in node.body],
            orelse=[from_builtin(x) for x in node.orelse],
        )

    def _transform(self, node_transformer, context):
        return While(
            test=node_transformer(self.test, context),
            body=[node_transformer(x, context) for x in self.body],
            orelse=[node_transformer(x, context) for x in self.orelse],
        )

    def _nodes_iter(self):
        yield self
        yield from self.test._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.orelse:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class If(stmt):
    test: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.If(
            test=to_builtin(self.test),
            body=[to_builtin(x) for x in self.body],
            orelse=[to_builtin(x) for x in self.orelse],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            test=from_builtin(node.test),
            body=[from_builtin(x) for x in node.body],
            orelse=[from_builtin(x) for x in node.orelse],
        )

    def _transform(self, node_transformer, context):
        return If(
            test=node_transformer(self.test, context),
            body=[node_transformer(x, context) for x in self.body],
            orelse=[node_transformer(x, context) for x in self.orelse],
        )

    def _nodes_iter(self):
        yield self
        yield from self.test._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.orelse:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class With(stmt):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    items: Sequence[withitem] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: withitem)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.With(
            body=[to_builtin(x) for x in self.body],
            items=[to_builtin(x) for x in self.items],
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=[from_builtin(x) for x in node.body],
            items=[from_builtin(x) for x in node.items],
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return With(
            body=[node_transformer(x, context) for x in self.body],
            items=[node_transformer(x, context) for x in self.items],
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.items:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class AsyncWith(stmt):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    items: Sequence[withitem] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: withitem)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.AsyncWith(
            body=[to_builtin(x) for x in self.body],
            items=[to_builtin(x) for x in self.items],
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=[from_builtin(x) for x in node.body],
            items=[from_builtin(x) for x in node.items],
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return AsyncWith(
            body=[node_transformer(x, context) for x in self.body],
            items=[node_transformer(x, context) for x in self.items],
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.items:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Match(stmt):
    subject: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    cases: Sequence[match_case] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: match_case)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Match(
            subject=to_builtin(self.subject), cases=[to_builtin(x) for x in self.cases]
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            subject=from_builtin(node.subject),
            cases=[from_builtin(x) for x in node.cases],
        )

    def _transform(self, node_transformer, context):
        return Match(
            subject=node_transformer(self.subject, context),
            cases=[node_transformer(x, context) for x in self.cases],
        )

    def _nodes_iter(self):
        yield self
        yield from self.subject._nodes_iter()
        for x in self.cases:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Raise(stmt):
    cause: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )
    exc: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.Raise(
            cause=None if self.cause is None else to_builtin(self.cause),
            exc=None if self.exc is None else to_builtin(self.exc),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            cause=None if node.cause is None else from_builtin(node.cause),
            exc=None if node.exc is None else from_builtin(node.exc),
        )

    def _transform(self, node_transformer, context):
        return Raise(
            cause=None if self.cause is None else node_transformer(self.cause, context),
            exc=None if self.exc is None else node_transformer(self.exc, context),
        )

    def _nodes_iter(self):
        yield self
        if self.cause is not None:
            yield from self.cause._nodes_iter()
        if self.exc is not None:
            yield from self.exc._nodes_iter()


@attrs.define()
class Try(stmt):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    finalbody: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    handlers: Sequence[excepthandler] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: excepthandler)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    orelse: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Try(
            body=[to_builtin(x) for x in self.body],
            finalbody=[to_builtin(x) for x in self.finalbody],
            handlers=[to_builtin(x) for x in self.handlers],
            orelse=[to_builtin(x) for x in self.orelse],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=[from_builtin(x) for x in node.body],
            finalbody=[from_builtin(x) for x in node.finalbody],
            handlers=[from_builtin(x) for x in node.handlers],
            orelse=[from_builtin(x) for x in node.orelse],
        )

    def _transform(self, node_transformer, context):
        return Try(
            body=[node_transformer(x, context) for x in self.body],
            finalbody=[node_transformer(x, context) for x in self.finalbody],
            handlers=[node_transformer(x, context) for x in self.handlers],
            orelse=[node_transformer(x, context) for x in self.orelse],
        )

    def _nodes_iter(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.finalbody:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.handlers:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.orelse:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Assert(stmt):
    test: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    msg: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.Assert(
            test=to_builtin(self.test),
            msg=None if self.msg is None else to_builtin(self.msg),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            test=from_builtin(node.test),
            msg=None if node.msg is None else from_builtin(node.msg),
        )

    def _transform(self, node_transformer, context):
        return Assert(
            test=node_transformer(self.test, context),
            msg=None if self.msg is None else node_transformer(self.msg, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.test._nodes_iter()
        if self.msg is not None:
            yield from self.msg._nodes_iter()


@attrs.define()
class Import(stmt):
    names: Sequence[alias] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: alias)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Import(names=[to_builtin(x) for x in self.names])

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=[from_builtin(x) for x in node.names])

    def _transform(self, node_transformer, context):
        return Import(names=[node_transformer(x, context) for x in self.names])

    def _nodes_iter(self):
        yield self
        for x in self.names:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class ImportFrom(stmt):
    level: Optional[int] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: int)),
        default=None,
    )
    module: Optional[str] = attrs.field(
        converter=attrs.converters.optional(convert_identifier), default=None
    )
    names: Sequence[alias] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: alias)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.ImportFrom(
            level=self.level,
            module=self.module,
            names=[to_builtin(x) for x in self.names],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            level=node.level,
            module=node.module,
            names=[from_builtin(x) for x in node.names],
        )

    def _transform(self, node_transformer, context):
        return ImportFrom(
            level=self.level,
            module=self.module,
            names=[node_transformer(x, context) for x in self.names],
        )

    def _nodes_iter(self):
        yield self
        for x in self.names:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Global(stmt):
    names: Sequence[str] = attrs.field(
        converter=DeepIterableConverter(convert_identifier), factory=list
    )

    def _to_builtin(self):
        return ast.Global(names=self.names)

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node.names)

    def _transform(self, node_transformer, context):
        return Global(names=self.names)

    def _nodes_iter(self):
        yield self


@attrs.define()
class Nonlocal(stmt):
    names: Sequence[str] = attrs.field(
        converter=DeepIterableConverter(convert_identifier), factory=list
    )

    def _to_builtin(self):
        return ast.Nonlocal(names=self.names)

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node.names)

    def _transform(self, node_transformer, context):
        return Nonlocal(names=self.names)

    def _nodes_iter(self):
        yield self


@attrs.define()
class Expr(stmt):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.Expr(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return Expr(value=node_transformer(self.value, context))

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()


@attrs.define()
class Pass(stmt):
    def _to_builtin(self):
        return ast.Pass()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Pass()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Break(stmt):
    def _to_builtin(self):
        return ast.Break()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Break()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Continue(stmt):
    def _to_builtin(self):
        return ast.Continue()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Continue()

    def _nodes_iter(self):
        yield self


class expr(Node):
    def __call__(self, *attrs):
        ret = self
        for name in reversed(attrs):
            ret = Attribute(value=ret, attr=name)
        return BoundUnderscore(ret)


@attrs.define()
class BoolOp(expr):
    op: boolop = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: boolop), converter=unwrap_underscore
    )
    values: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.BoolOp(
            op=to_builtin(self.op), values=[to_builtin(x) for x in self.values]
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            op=from_builtin(node.op), values=[from_builtin(x) for x in node.values]
        )

    def _transform(self, node_transformer, context):
        return BoolOp(
            op=node_transformer(self.op, context),
            values=[node_transformer(x, context) for x in self.values],
        )

    def _nodes_iter(self):
        yield self
        yield from self.op._nodes_iter()
        for x in self.values:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class NamedExpr(expr):
    target: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.NamedExpr(
            target=to_builtin(self.target), value=to_builtin(self.value)
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=from_builtin(node.target), value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return NamedExpr(
            target=node_transformer(self.target, context),
            value=node_transformer(self.value, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.target._nodes_iter()
        yield from self.value._nodes_iter()


@attrs.define()
class BinOp(expr):
    left: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    op: operator = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: operator),
        converter=unwrap_underscore,
    )
    right: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.BinOp(
            left=to_builtin(self.left),
            op=to_builtin(self.op),
            right=to_builtin(self.right),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            left=from_builtin(node.left),
            op=from_builtin(node.op),
            right=from_builtin(node.right),
        )

    def _transform(self, node_transformer, context):
        return BinOp(
            left=node_transformer(self.left, context),
            op=node_transformer(self.op, context),
            right=node_transformer(self.right, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.left._nodes_iter()
        yield from self.op._nodes_iter()
        yield from self.right._nodes_iter()


@attrs.define()
class UnaryOp(expr):
    op: unaryop = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: unaryop), converter=unwrap_underscore
    )
    operand: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.UnaryOp(op=to_builtin(self.op), operand=to_builtin(self.operand))

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=from_builtin(node.op), operand=from_builtin(node.operand))

    def _transform(self, node_transformer, context):
        return UnaryOp(
            op=node_transformer(self.op, context),
            operand=node_transformer(self.operand, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.op._nodes_iter()
        yield from self.operand._nodes_iter()


@attrs.define()
class Lambda(expr):
    args: arguments = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: arguments),
        converter=unwrap_underscore,
    )
    body: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.Lambda(args=to_builtin(self.args), body=to_builtin(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(args=from_builtin(node.args), body=from_builtin(node.body))

    def _transform(self, node_transformer, context):
        return Lambda(
            args=node_transformer(self.args, context),
            body=node_transformer(self.body, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.args._nodes_iter()
        yield from self.body._nodes_iter()


@attrs.define()
class IfExp(expr):
    body: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    orelse: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    test: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.IfExp(
            body=to_builtin(self.body),
            orelse=to_builtin(self.orelse),
            test=to_builtin(self.test),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=from_builtin(node.body),
            orelse=from_builtin(node.orelse),
            test=from_builtin(node.test),
        )

    def _transform(self, node_transformer, context):
        return IfExp(
            body=node_transformer(self.body, context),
            orelse=node_transformer(self.orelse, context),
            test=node_transformer(self.test, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.body._nodes_iter()
        yield from self.orelse._nodes_iter()
        yield from self.test._nodes_iter()


@attrs.define()
class Dict(expr):
    keys: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    values: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Dict(
            keys=[to_builtin(x) for x in self.keys],
            values=[to_builtin(x) for x in self.values],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            keys=[from_builtin(x) for x in node.keys],
            values=[from_builtin(x) for x in node.values],
        )

    def _transform(self, node_transformer, context):
        return Dict(
            keys=[node_transformer(x, context) for x in self.keys],
            values=[node_transformer(x, context) for x in self.values],
        )

    def _nodes_iter(self):
        yield self
        for x in self.keys:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.values:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Set(expr):
    elts: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Set(elts=[to_builtin(x) for x in self.elts])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=[from_builtin(x) for x in node.elts])

    def _transform(self, node_transformer, context):
        return Set(elts=[node_transformer(x, context) for x in self.elts])

    def _nodes_iter(self):
        yield self
        for x in self.elts:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class ListComp(expr):
    elt: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.ListComp(
            elt=to_builtin(self.elt),
            generators=[to_builtin(x) for x in self.generators],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            elt=from_builtin(node.elt),
            generators=[from_builtin(x) for x in node.generators],
        )

    def _transform(self, node_transformer, context):
        return ListComp(
            elt=node_transformer(self.elt, context),
            generators=[node_transformer(x, context) for x in self.generators],
        )

    def _nodes_iter(self):
        yield self
        yield from self.elt._nodes_iter()
        for x in self.generators:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class SetComp(expr):
    elt: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.SetComp(
            elt=to_builtin(self.elt),
            generators=[to_builtin(x) for x in self.generators],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            elt=from_builtin(node.elt),
            generators=[from_builtin(x) for x in node.generators],
        )

    def _transform(self, node_transformer, context):
        return SetComp(
            elt=node_transformer(self.elt, context),
            generators=[node_transformer(x, context) for x in self.generators],
        )

    def _nodes_iter(self):
        yield self
        yield from self.elt._nodes_iter()
        for x in self.generators:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class DictComp(expr):
    key: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.DictComp(
            key=to_builtin(self.key),
            value=to_builtin(self.value),
            generators=[to_builtin(x) for x in self.generators],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            key=from_builtin(node.key),
            value=from_builtin(node.value),
            generators=[from_builtin(x) for x in node.generators],
        )

    def _transform(self, node_transformer, context):
        return DictComp(
            key=node_transformer(self.key, context),
            value=node_transformer(self.value, context),
            generators=[node_transformer(x, context) for x in self.generators],
        )

    def _nodes_iter(self):
        yield self
        yield from self.key._nodes_iter()
        yield from self.value._nodes_iter()
        for x in self.generators:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class GeneratorExp(expr):
    elt: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    generators: Sequence[comprehension] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: comprehension)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.GeneratorExp(
            elt=to_builtin(self.elt),
            generators=[to_builtin(x) for x in self.generators],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            elt=from_builtin(node.elt),
            generators=[from_builtin(x) for x in node.generators],
        )

    def _transform(self, node_transformer, context):
        return GeneratorExp(
            elt=node_transformer(self.elt, context),
            generators=[node_transformer(x, context) for x in self.generators],
        )

    def _nodes_iter(self):
        yield self
        yield from self.elt._nodes_iter()
        for x in self.generators:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Await(expr):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.Await(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return Await(value=node_transformer(self.value, context))

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()


@attrs.define()
class Yield(expr):
    value: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.Yield(value=None if self.value is None else to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=None if node.value is None else from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return Yield(
            value=None if self.value is None else node_transformer(self.value, context)
        )

    def _nodes_iter(self):
        yield self
        if self.value is not None:
            yield from self.value._nodes_iter()


@attrs.define()
class YieldFrom(expr):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.YieldFrom(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return YieldFrom(value=node_transformer(self.value, context))

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()


@attrs.define()
class Compare(expr):
    left: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    comparators: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    ops: Sequence[cmpop] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: cmpop)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Compare(
            left=to_builtin(self.left),
            comparators=[to_builtin(x) for x in self.comparators],
            ops=[to_builtin(x) for x in self.ops],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            left=from_builtin(node.left),
            comparators=[from_builtin(x) for x in node.comparators],
            ops=[from_builtin(x) for x in node.ops],
        )

    def _transform(self, node_transformer, context):
        return Compare(
            left=node_transformer(self.left, context),
            comparators=[node_transformer(x, context) for x in self.comparators],
            ops=[node_transformer(x, context) for x in self.ops],
        )

    def _nodes_iter(self):
        yield self
        yield from self.left._nodes_iter()
        for x in self.comparators:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.ops:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Call(expr):
    func: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    args: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    keywords: Sequence[keyword] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: keyword)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Call(
            func=to_builtin(self.func),
            args=[to_builtin(x) for x in self.args],
            keywords=[to_builtin(x) for x in self.keywords],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            func=from_builtin(node.func),
            args=[from_builtin(x) for x in node.args],
            keywords=[from_builtin(x) for x in node.keywords],
        )

    def _transform(self, node_transformer, context):
        return Call(
            func=node_transformer(self.func, context),
            args=[node_transformer(x, context) for x in self.args],
            keywords=[node_transformer(x, context) for x in self.keywords],
        )

    def _nodes_iter(self):
        yield self
        yield from self.func._nodes_iter()
        for x in self.args:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.keywords:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class FormattedValue(expr):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    conversion: Optional[int] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: int)),
        default=None,
    )
    format_spec: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.FormattedValue(
            value=to_builtin(self.value),
            conversion=self.conversion,
            format_spec=None
            if self.format_spec is None
            else to_builtin(self.format_spec),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            value=from_builtin(node.value),
            conversion=node.conversion,
            format_spec=None
            if node.format_spec is None
            else from_builtin(node.format_spec),
        )

    def _transform(self, node_transformer, context):
        return FormattedValue(
            value=node_transformer(self.value, context),
            conversion=self.conversion,
            format_spec=None
            if self.format_spec is None
            else node_transformer(self.format_spec, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()
        if self.format_spec is not None:
            yield from self.format_spec._nodes_iter()


@attrs.define()
class JoinedStr(expr):
    values: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.JoinedStr(values=[to_builtin(x) for x in self.values])

    @classmethod
    def _from_builtin(cls, node):
        return cls(values=[from_builtin(x) for x in node.values])

    def _transform(self, node_transformer, context):
        return JoinedStr(values=[node_transformer(x, context) for x in self.values])

    def _nodes_iter(self):
        yield self
        for x in self.values:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Constant(expr):
    value: Any = attrs.field()
    kind: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
    )

    def _to_builtin(self):
        return ast.Constant(value=self.value, kind=self.kind)

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node.value, kind=node.kind)

    def _transform(self, node_transformer, context):
        return Constant(value=self.value, kind=self.kind)

    def _nodes_iter(self):
        yield self


@attrs.define()
class Attribute(expr):
    attr: str = attrs.field(converter=convert_identifier)
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.Attribute(attr=self.attr, value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(attr=node.attr, value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return Attribute(attr=self.attr, value=node_transformer(self.value, context))

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()


@attrs.define()
class Subscript(expr):
    slice: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.Subscript(slice=to_builtin(self.slice), value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(slice=from_builtin(node.slice), value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return Subscript(
            slice=node_transformer(self.slice, context),
            value=node_transformer(self.value, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.slice._nodes_iter()
        yield from self.value._nodes_iter()


@attrs.define()
class Starred(expr):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.Starred(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return Starred(value=node_transformer(self.value, context))

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()


@attrs.define()
class Name(expr):
    id: str = attrs.field(converter=convert_identifier)

    def _to_builtin(self):
        return ast.Name(id=self.id)

    @classmethod
    def _from_builtin(cls, node):
        return cls(id=node.id)

    def _transform(self, node_transformer, context):
        return Name(id=self.id)

    def _nodes_iter(self):
        yield self


@attrs.define()
class List(expr):
    elts: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.List(elts=[to_builtin(x) for x in self.elts])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=[from_builtin(x) for x in node.elts])

    def _transform(self, node_transformer, context):
        return List(elts=[node_transformer(x, context) for x in self.elts])

    def _nodes_iter(self):
        yield self
        for x in self.elts:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Tuple(expr):
    elts: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.Tuple(elts=[to_builtin(x) for x in self.elts])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=[from_builtin(x) for x in node.elts])

    def _transform(self, node_transformer, context):
        return Tuple(elts=[node_transformer(x, context) for x in self.elts])

    def _nodes_iter(self):
        yield self
        for x in self.elts:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class Slice(expr):
    lower: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )
    step: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )
    upper: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.Slice(
            lower=None if self.lower is None else to_builtin(self.lower),
            step=None if self.step is None else to_builtin(self.step),
            upper=None if self.upper is None else to_builtin(self.upper),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            lower=None if node.lower is None else from_builtin(node.lower),
            step=None if node.step is None else from_builtin(node.step),
            upper=None if node.upper is None else from_builtin(node.upper),
        )

    def _transform(self, node_transformer, context):
        return Slice(
            lower=None if self.lower is None else node_transformer(self.lower, context),
            step=None if self.step is None else node_transformer(self.step, context),
            upper=None if self.upper is None else node_transformer(self.upper, context),
        )

    def _nodes_iter(self):
        yield self
        if self.lower is not None:
            yield from self.lower._nodes_iter()
        if self.step is not None:
            yield from self.step._nodes_iter()
        if self.upper is not None:
            yield from self.upper._nodes_iter()


class expr_context(Node):
    pass


@attrs.define()
class Load(expr_context):
    def _to_builtin(self):
        return ast.Load()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Load()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Store(expr_context):
    def _to_builtin(self):
        return ast.Store()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Store()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Del(expr_context):
    def _to_builtin(self):
        return ast.Del()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Del()

    def _nodes_iter(self):
        yield self


class boolop(Node):
    pass


@attrs.define()
class And(boolop):
    def _to_builtin(self):
        return ast.And()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return And()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Or(boolop):
    def _to_builtin(self):
        return ast.Or()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Or()

    def _nodes_iter(self):
        yield self


class operator(Node):
    pass


@attrs.define()
class Add(operator):
    def _to_builtin(self):
        return ast.Add()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Add()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Sub(operator):
    def _to_builtin(self):
        return ast.Sub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Sub()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Mult(operator):
    def _to_builtin(self):
        return ast.Mult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Mult()

    def _nodes_iter(self):
        yield self


@attrs.define()
class MatMult(operator):
    def _to_builtin(self):
        return ast.MatMult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return MatMult()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Div(operator):
    def _to_builtin(self):
        return ast.Div()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Div()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Mod(operator):
    def _to_builtin(self):
        return ast.Mod()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Mod()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Pow(operator):
    def _to_builtin(self):
        return ast.Pow()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Pow()

    def _nodes_iter(self):
        yield self


@attrs.define()
class LShift(operator):
    def _to_builtin(self):
        return ast.LShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return LShift()

    def _nodes_iter(self):
        yield self


@attrs.define()
class RShift(operator):
    def _to_builtin(self):
        return ast.RShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return RShift()

    def _nodes_iter(self):
        yield self


@attrs.define()
class BitOr(operator):
    def _to_builtin(self):
        return ast.BitOr()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return BitOr()

    def _nodes_iter(self):
        yield self


@attrs.define()
class BitXor(operator):
    def _to_builtin(self):
        return ast.BitXor()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return BitXor()

    def _nodes_iter(self):
        yield self


@attrs.define()
class BitAnd(operator):
    def _to_builtin(self):
        return ast.BitAnd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return BitAnd()

    def _nodes_iter(self):
        yield self


@attrs.define()
class FloorDiv(operator):
    def _to_builtin(self):
        return ast.FloorDiv()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return FloorDiv()

    def _nodes_iter(self):
        yield self


class unaryop(Node):
    pass


@attrs.define()
class Invert(unaryop):
    def _to_builtin(self):
        return ast.Invert()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Invert()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Not(unaryop):
    def _to_builtin(self):
        return ast.Not()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Not()

    def _nodes_iter(self):
        yield self


@attrs.define()
class UAdd(unaryop):
    def _to_builtin(self):
        return ast.UAdd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return UAdd()

    def _nodes_iter(self):
        yield self


@attrs.define()
class USub(unaryop):
    def _to_builtin(self):
        return ast.USub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return USub()

    def _nodes_iter(self):
        yield self


class cmpop(Node):
    pass


@attrs.define()
class Eq(cmpop):
    def _to_builtin(self):
        return ast.Eq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Eq()

    def _nodes_iter(self):
        yield self


@attrs.define()
class NotEq(cmpop):
    def _to_builtin(self):
        return ast.NotEq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return NotEq()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Lt(cmpop):
    def _to_builtin(self):
        return ast.Lt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Lt()

    def _nodes_iter(self):
        yield self


@attrs.define()
class LtE(cmpop):
    def _to_builtin(self):
        return ast.LtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return LtE()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Gt(cmpop):
    def _to_builtin(self):
        return ast.Gt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Gt()

    def _nodes_iter(self):
        yield self


@attrs.define()
class GtE(cmpop):
    def _to_builtin(self):
        return ast.GtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return GtE()

    def _nodes_iter(self):
        yield self


@attrs.define()
class Is(cmpop):
    def _to_builtin(self):
        return ast.Is()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return Is()

    def _nodes_iter(self):
        yield self


@attrs.define()
class IsNot(cmpop):
    def _to_builtin(self):
        return ast.IsNot()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return IsNot()

    def _nodes_iter(self):
        yield self


@attrs.define()
class In(cmpop):
    def _to_builtin(self):
        return ast.In()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return In()

    def _nodes_iter(self):
        yield self


@attrs.define()
class NotIn(cmpop):
    def _to_builtin(self):
        return ast.NotIn()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        return NotIn()

    def _nodes_iter(self):
        yield self


@attrs.define()
class comprehension(Node):
    is_async: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    iter: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    target: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    ifs: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.comprehension(
            is_async=self.is_async,
            iter=to_builtin(self.iter),
            target=to_builtin(self.target),
            ifs=[to_builtin(x) for x in self.ifs],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            is_async=node.is_async,
            iter=from_builtin(node.iter),
            target=from_builtin(node.target),
            ifs=[from_builtin(x) for x in node.ifs],
        )

    def _transform(self, node_transformer, context):
        return comprehension(
            is_async=self.is_async,
            iter=node_transformer(self.iter, context),
            target=node_transformer(self.target, context),
            ifs=[node_transformer(x, context) for x in self.ifs],
        )

    def _nodes_iter(self):
        yield self
        yield from self.iter._nodes_iter()
        yield from self.target._nodes_iter()
        for x in self.ifs:
            if x is not None:
                yield from x._nodes_iter()


class excepthandler(Node):
    pass


@attrs.define()
class ExceptHandler(excepthandler):
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    name: Optional[str] = attrs.field(
        converter=attrs.converters.optional(convert_identifier), default=None
    )
    type: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.ExceptHandler(
            body=[to_builtin(x) for x in self.body],
            name=self.name,
            type=None if self.type is None else to_builtin(self.type),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            body=[from_builtin(x) for x in node.body],
            name=node.name,
            type=None if node.type is None else from_builtin(node.type),
        )

    def _transform(self, node_transformer, context):
        return ExceptHandler(
            body=[node_transformer(x, context) for x in self.body],
            name=self.name,
            type=None if self.type is None else node_transformer(self.type, context),
        )

    def _nodes_iter(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        if self.type is not None:
            yield from self.type._nodes_iter()


@attrs.define()
class arguments(Node):
    args: Sequence[arg] = attrs.field(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    defaults: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    kw_defaults: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    kwarg: Optional[arg] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: arg)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )
    kwonlyargs: Sequence[arg] = attrs.field(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    posonlyargs: Sequence[arg] = attrs.field(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    vararg: Optional[arg] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: arg)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.arguments(
            args=[to_builtin(x) for x in self.args],
            defaults=[to_builtin(x) for x in self.defaults],
            kw_defaults=[to_builtin(x) for x in self.kw_defaults],
            kwarg=None if self.kwarg is None else to_builtin(self.kwarg),
            kwonlyargs=[to_builtin(x) for x in self.kwonlyargs],
            posonlyargs=[to_builtin(x) for x in self.posonlyargs],
            vararg=None if self.vararg is None else to_builtin(self.vararg),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            args=[from_builtin(x) for x in node.args],
            defaults=[from_builtin(x) for x in node.defaults],
            kw_defaults=[from_builtin(x) for x in node.kw_defaults],
            kwarg=None if node.kwarg is None else from_builtin(node.kwarg),
            kwonlyargs=[from_builtin(x) for x in node.kwonlyargs],
            posonlyargs=[from_builtin(x) for x in node.posonlyargs],
            vararg=None if node.vararg is None else from_builtin(node.vararg),
        )

    def _transform(self, node_transformer, context):
        return arguments(
            args=[node_transformer(x, context) for x in self.args],
            defaults=[node_transformer(x, context) for x in self.defaults],
            kw_defaults=[node_transformer(x, context) for x in self.kw_defaults],
            kwarg=None if self.kwarg is None else node_transformer(self.kwarg, context),
            kwonlyargs=[node_transformer(x, context) for x in self.kwonlyargs],
            posonlyargs=[node_transformer(x, context) for x in self.posonlyargs],
            vararg=None
            if self.vararg is None
            else node_transformer(self.vararg, context),
        )

    def _nodes_iter(self):
        yield self
        for x in self.args:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.defaults:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.kw_defaults:
            if x is not None:
                yield from x._nodes_iter()
        if self.kwarg is not None:
            yield from self.kwarg._nodes_iter()
        for x in self.kwonlyargs:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.posonlyargs:
            if x is not None:
                yield from x._nodes_iter()
        if self.vararg is not None:
            yield from self.vararg._nodes_iter()


@attrs.define()
class arg(Node):
    arg: str = attrs.field(converter=convert_identifier)
    annotation: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )
    type_comment: Optional[str] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)),
        default=None,
        repr=False,
    )

    def _to_builtin(self):
        return ast.arg(
            arg=self.arg,
            annotation=None if self.annotation is None else to_builtin(self.annotation),
            type_comment=self.type_comment,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            arg=node.arg,
            annotation=None
            if node.annotation is None
            else from_builtin(node.annotation),
            type_comment=node.type_comment,
        )

    def _transform(self, node_transformer, context):
        return arg(
            arg=self.arg,
            annotation=None
            if self.annotation is None
            else node_transformer(self.annotation, context),
            type_comment=self.type_comment,
        )

    def _nodes_iter(self):
        yield self
        if self.annotation is not None:
            yield from self.annotation._nodes_iter()


@attrs.define()
class keyword(Node):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    arg: Optional[str] = attrs.field(
        converter=attrs.converters.optional(convert_identifier), default=None
    )

    def _to_builtin(self):
        return ast.keyword(value=to_builtin(self.value), arg=self.arg)

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value), arg=node.arg)

    def _transform(self, node_transformer, context):
        return keyword(value=node_transformer(self.value, context), arg=self.arg)

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()


@attrs.define()
class alias(Node):
    name: str = attrs.field(converter=convert_identifier)
    asname: Optional[str] = attrs.field(
        converter=attrs.converters.optional(convert_identifier), default=None
    )

    def _to_builtin(self):
        return ast.alias(name=self.name, asname=self.asname)

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node.name, asname=node.asname)

    def _transform(self, node_transformer, context):
        return alias(name=self.name, asname=self.asname)

    def _nodes_iter(self):
        yield self


@attrs.define()
class withitem(Node):
    context_expr: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    optional_vars: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.withitem(
            context_expr=to_builtin(self.context_expr),
            optional_vars=None
            if self.optional_vars is None
            else to_builtin(self.optional_vars),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            context_expr=from_builtin(node.context_expr),
            optional_vars=None
            if node.optional_vars is None
            else from_builtin(node.optional_vars),
        )

    def _transform(self, node_transformer, context):
        return withitem(
            context_expr=node_transformer(self.context_expr, context),
            optional_vars=None
            if self.optional_vars is None
            else node_transformer(self.optional_vars, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.context_expr._nodes_iter()
        if self.optional_vars is not None:
            yield from self.optional_vars._nodes_iter()


@attrs.define()
class match_case(Node):
    pattern: pattern = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: pattern), converter=unwrap_underscore
    )
    body: Sequence[stmt] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: stmt)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    guard: Optional[expr] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.match_case(
            pattern=to_builtin(self.pattern),
            body=[to_builtin(x) for x in self.body],
            guard=None if self.guard is None else to_builtin(self.guard),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            pattern=from_builtin(node.pattern),
            body=[from_builtin(x) for x in node.body],
            guard=None if node.guard is None else from_builtin(node.guard),
        )

    def _transform(self, node_transformer, context):
        return match_case(
            pattern=node_transformer(self.pattern, context),
            body=[node_transformer(x, context) for x in self.body],
            guard=None if self.guard is None else node_transformer(self.guard, context),
        )

    def _nodes_iter(self):
        yield self
        yield from self.pattern._nodes_iter()
        for x in self.body:
            if x is not None:
                yield from x._nodes_iter()
        if self.guard is not None:
            yield from self.guard._nodes_iter()


class pattern(Node):
    pass


@attrs.define()
class MatchValue(pattern):
    value: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )

    def _to_builtin(self):
        return ast.MatchValue(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        return MatchValue(value=node_transformer(self.value, context))

    def _nodes_iter(self):
        yield self
        yield from self.value._nodes_iter()


@attrs.define()
class MatchSingleton(pattern):
    value: Any = attrs.field()

    def _to_builtin(self):
        return ast.MatchSingleton(value=self.value)

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node.value)

    def _transform(self, node_transformer, context):
        return MatchSingleton(value=self.value)

    def _nodes_iter(self):
        yield self


@attrs.define()
class MatchSequence(pattern):
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.MatchSequence(patterns=[to_builtin(x) for x in self.patterns])

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=[from_builtin(x) for x in node.patterns])

    def _transform(self, node_transformer, context):
        return MatchSequence(
            patterns=[node_transformer(x, context) for x in self.patterns]
        )

    def _nodes_iter(self):
        yield self
        for x in self.patterns:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class MatchMapping(pattern):
    keys: Sequence[expr] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: expr)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    rest: Optional[str] = attrs.field(
        converter=attrs.converters.optional(convert_identifier), default=None
    )

    def _to_builtin(self):
        return ast.MatchMapping(
            keys=[to_builtin(x) for x in self.keys],
            patterns=[to_builtin(x) for x in self.patterns],
            rest=self.rest,
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            keys=[from_builtin(x) for x in node.keys],
            patterns=[from_builtin(x) for x in node.patterns],
            rest=node.rest,
        )

    def _transform(self, node_transformer, context):
        return MatchMapping(
            keys=[node_transformer(x, context) for x in self.keys],
            patterns=[node_transformer(x, context) for x in self.patterns],
            rest=self.rest,
        )

    def _nodes_iter(self):
        yield self
        for x in self.keys:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.patterns:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class MatchClass(pattern):
    cls: expr = attrs.field(
        validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore
    )
    kwd_attrs: Sequence[str] = attrs.field(
        converter=DeepIterableConverter(convert_identifier), factory=list
    )
    kwd_patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.MatchClass(
            cls=to_builtin(self.cls),
            kwd_attrs=self.kwd_attrs,
            kwd_patterns=[to_builtin(x) for x in self.kwd_patterns],
            patterns=[to_builtin(x) for x in self.patterns],
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            cls=from_builtin(node.cls),
            kwd_attrs=node.kwd_attrs,
            kwd_patterns=[from_builtin(x) for x in node.kwd_patterns],
            patterns=[from_builtin(x) for x in node.patterns],
        )

    def _transform(self, node_transformer, context):
        return MatchClass(
            cls=node_transformer(self.cls, context),
            kwd_attrs=self.kwd_attrs,
            kwd_patterns=[node_transformer(x, context) for x in self.kwd_patterns],
            patterns=[node_transformer(x, context) for x in self.patterns],
        )

    def _nodes_iter(self):
        yield self
        yield from self.cls._nodes_iter()
        for x in self.kwd_patterns:
            if x is not None:
                yield from x._nodes_iter()
        for x in self.patterns:
            if x is not None:
                yield from x._nodes_iter()


@attrs.define()
class MatchStar(pattern):
    name: Optional[str] = attrs.field(
        converter=attrs.converters.optional(convert_identifier), default=None
    )

    def _to_builtin(self):
        return ast.MatchStar(name=self.name)

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node.name)

    def _transform(self, node_transformer, context):
        return MatchStar(name=self.name)

    def _nodes_iter(self):
        yield self


@attrs.define()
class MatchAs(pattern):
    name: Optional[str] = attrs.field(
        converter=attrs.converters.optional(convert_identifier), default=None
    )
    pattern: Optional[pattern] = attrs.field(
        validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: pattern)),
        converter=attrs.converters.optional(unwrap_underscore),
        default=None,
    )

    def _to_builtin(self):
        return ast.MatchAs(
            name=self.name,
            pattern=None if self.pattern is None else to_builtin(self.pattern),
        )

    @classmethod
    def _from_builtin(cls, node):
        return cls(
            name=node.name,
            pattern=None if node.pattern is None else from_builtin(node.pattern),
        )

    def _transform(self, node_transformer, context):
        return MatchAs(
            name=self.name,
            pattern=None
            if self.pattern is None
            else node_transformer(self.pattern, context),
        )

    def _nodes_iter(self):
        yield self
        if self.pattern is not None:
            yield from self.pattern._nodes_iter()


@attrs.define()
class MatchOr(pattern):
    patterns: Sequence[pattern] = attrs.field(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: pattern)
        ),
        converter=DeepIterableConverter(unwrap_underscore),
        factory=list,
    )

    def _to_builtin(self):
        return ast.MatchOr(patterns=[to_builtin(x) for x in self.patterns])

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=[from_builtin(x) for x in node.patterns])

    def _transform(self, node_transformer, context):
        return MatchOr(patterns=[node_transformer(x, context) for x in self.patterns])

    def _nodes_iter(self):
        yield self
        for x in self.patterns:
            if x is not None:
                yield from x._nodes_iter()


class type_ignore(Node):
    pass


@attrs.define()
class TypeIgnore(type_ignore):
    lineno: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    tag: str = attrs.field(validator=ProxyInstanceOfValidator(lambda: str))

    def _to_builtin(self):
        return ast.TypeIgnore(lineno=self.lineno, tag=self.tag)

    @classmethod
    def _from_builtin(cls, node):
        return cls(lineno=node.lineno, tag=node.tag)

    def _transform(self, node_transformer, context):
        return TypeIgnore(lineno=self.lineno, tag=self.tag)

    def _nodes_iter(self):
        yield self


NODES = dict(
    Module=Module,
    Interactive=Interactive,
    Expression=Expression,
    FunctionType=FunctionType,
    FunctionDef=FunctionDef,
    AsyncFunctionDef=AsyncFunctionDef,
    ClassDef=ClassDef,
    Return=Return,
    Delete=Delete,
    Assign=Assign,
    AugAssign=AugAssign,
    AnnAssign=AnnAssign,
    For=For,
    AsyncFor=AsyncFor,
    While=While,
    If=If,
    With=With,
    AsyncWith=AsyncWith,
    Match=Match,
    Raise=Raise,
    Try=Try,
    Assert=Assert,
    Import=Import,
    ImportFrom=ImportFrom,
    Global=Global,
    Nonlocal=Nonlocal,
    Expr=Expr,
    Pass=Pass,
    Break=Break,
    Continue=Continue,
    BoolOp=BoolOp,
    NamedExpr=NamedExpr,
    BinOp=BinOp,
    UnaryOp=UnaryOp,
    Lambda=Lambda,
    IfExp=IfExp,
    Dict=Dict,
    Set=Set,
    ListComp=ListComp,
    SetComp=SetComp,
    DictComp=DictComp,
    GeneratorExp=GeneratorExp,
    Await=Await,
    Yield=Yield,
    YieldFrom=YieldFrom,
    Compare=Compare,
    Call=Call,
    FormattedValue=FormattedValue,
    JoinedStr=JoinedStr,
    Constant=Constant,
    Attribute=Attribute,
    Subscript=Subscript,
    Starred=Starred,
    Name=Name,
    List=List,
    Tuple=Tuple,
    Slice=Slice,
    Load=Load,
    Store=Store,
    Del=Del,
    And=And,
    Or=Or,
    Add=Add,
    Sub=Sub,
    Mult=Mult,
    MatMult=MatMult,
    Div=Div,
    Mod=Mod,
    Pow=Pow,
    LShift=LShift,
    RShift=RShift,
    BitOr=BitOr,
    BitXor=BitXor,
    BitAnd=BitAnd,
    FloorDiv=FloorDiv,
    Invert=Invert,
    Not=Not,
    UAdd=UAdd,
    USub=USub,
    Eq=Eq,
    NotEq=NotEq,
    Lt=Lt,
    LtE=LtE,
    Gt=Gt,
    GtE=GtE,
    Is=Is,
    IsNot=IsNot,
    In=In,
    NotIn=NotIn,
    comprehension=comprehension,
    ExceptHandler=ExceptHandler,
    arguments=arguments,
    arg=arg,
    keyword=keyword,
    alias=alias,
    withitem=withitem,
    match_case=match_case,
    MatchValue=MatchValue,
    MatchSingleton=MatchSingleton,
    MatchSequence=MatchSequence,
    MatchMapping=MatchMapping,
    MatchClass=MatchClass,
    MatchStar=MatchStar,
    MatchAs=MatchAs,
    MatchOr=MatchOr,
    TypeIgnore=TypeIgnore,
)
