from __future__ import annotations
import ast
from typing import Callable, Optional, Sequence, Union
import attrs
from .common import Node, WrappedNode, TransformerContext
from .validators import DeepIterableConverter, ProxyInstanceOfValidator, convert_identifier, unwrap_underscore

def to_builtin(node: Node) -> ast.AST:
    match node:
        case WrappedNode():
            node = node.__inner__
        case Node():
            pass
        case other:
            raise TypeError('Wrong type')
    return node._to_builtin()

def from_builtin(node: ast.AST) -> Node:
    assert isinstance(node, ast.AST)
    t = node.__class__.__name__
    return NODES[t]._from_builtin(node)

class Node:
    pass

class mod(Node):
    pass

@attrs.frozen()
class Module(mod):
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    type_ignores: Sequence[type_ignore] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: type_ignore)), converter=DeepIterableConverter(unwrap_underscore), factory=list, repr=False)

    def _to_builtin(self):
        return ast.Module(body=[to_builtin(x) for x in self.body], type_ignores=[to_builtin(x) for x in self.type_ignores])

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=[from_builtin(x) for x in node.body], type_ignores=[from_builtin(x) for x in node.type_ignores])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Module(body=[x._transform(node_transformer, inner_context) for x in self.body], type_ignores=[x._transform(node_transformer, inner_context) for x in self.type_ignores])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.type_ignores:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Interactive(mod):
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Interactive(body=[to_builtin(x) for x in self.body])

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=[from_builtin(x) for x in node.body])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Interactive(body=[x._transform(node_transformer, inner_context) for x in self.body])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Expression(mod):
    body: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.Expression(body=to_builtin(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=from_builtin(node.body))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Expression(body=self.body._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.body()._children()

@attrs.frozen()
class FunctionType(mod):
    returns: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    argtypes: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.FunctionType(returns=to_builtin(self.returns), argtypes=[to_builtin(x) for x in self.argtypes])

    @classmethod
    def _from_builtin(cls, node):
        return cls(returns=from_builtin(node.returns), argtypes=[from_builtin(x) for x in node.argtypes])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = FunctionType(returns=self.returns._transform(node_transformer, inner_context), argtypes=[x._transform(node_transformer, inner_context) for x in self.argtypes])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.returns()._children()
        for x in self.argtypes:
            if x is not None:
                yield from x._children()

class stmt(Node):
    pass

@attrs.frozen()
class FunctionDef(stmt):
    args: arguments = attrs.field(validator=ProxyInstanceOfValidator(lambda: arguments), converter=unwrap_underscore)
    name: str = attrs.field(converter=convert_identifier)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    decorator_list: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    returns: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.FunctionDef(args=to_builtin(self.args), name=self.name, body=[to_builtin(x) for x in self.body], decorator_list=[to_builtin(x) for x in self.decorator_list], returns=None if self.returns is None else to_builtin(self.returns), type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(args=from_builtin(node.args), name=node.name, body=[from_builtin(x) for x in node.body], decorator_list=[from_builtin(x) for x in node.decorator_list], returns=None if node.returns is None else from_builtin(node.returns), type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = FunctionDef(args=self.args._transform(node_transformer, inner_context), name=self.name, body=[x._transform(node_transformer, inner_context) for x in self.body], decorator_list=[x._transform(node_transformer, inner_context) for x in self.decorator_list], returns=None if self.returns is None else self.returns._transform(node_transformer, inner_context), type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.args()._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.decorator_list:
            if x is not None:
                yield from x._children()
        if self.returns is not None:
            yield from self.returns()._children()

@attrs.frozen()
class AsyncFunctionDef(stmt):
    args: arguments = attrs.field(validator=ProxyInstanceOfValidator(lambda: arguments), converter=unwrap_underscore)
    name: str = attrs.field(converter=convert_identifier)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    decorator_list: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    returns: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.AsyncFunctionDef(args=to_builtin(self.args), name=self.name, body=[to_builtin(x) for x in self.body], decorator_list=[to_builtin(x) for x in self.decorator_list], returns=None if self.returns is None else to_builtin(self.returns), type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(args=from_builtin(node.args), name=node.name, body=[from_builtin(x) for x in node.body], decorator_list=[from_builtin(x) for x in node.decorator_list], returns=None if node.returns is None else from_builtin(node.returns), type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = AsyncFunctionDef(args=self.args._transform(node_transformer, inner_context), name=self.name, body=[x._transform(node_transformer, inner_context) for x in self.body], decorator_list=[x._transform(node_transformer, inner_context) for x in self.decorator_list], returns=None if self.returns is None else self.returns._transform(node_transformer, inner_context), type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.args()._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.decorator_list:
            if x is not None:
                yield from x._children()
        if self.returns is not None:
            yield from self.returns()._children()

@attrs.frozen()
class ClassDef(stmt):
    name: str = attrs.field(converter=convert_identifier)
    bases: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    decorator_list: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    keywords: Sequence[keyword] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: keyword)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.ClassDef(name=self.name, bases=[to_builtin(x) for x in self.bases], body=[to_builtin(x) for x in self.body], decorator_list=[to_builtin(x) for x in self.decorator_list], keywords=[to_builtin(x) for x in self.keywords])

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node.name, bases=[from_builtin(x) for x in node.bases], body=[from_builtin(x) for x in node.body], decorator_list=[from_builtin(x) for x in node.decorator_list], keywords=[from_builtin(x) for x in node.keywords])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = ClassDef(name=self.name, bases=[x._transform(node_transformer, inner_context) for x in self.bases], body=[x._transform(node_transformer, inner_context) for x in self.body], decorator_list=[x._transform(node_transformer, inner_context) for x in self.decorator_list], keywords=[x._transform(node_transformer, inner_context) for x in self.keywords])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.bases:
            if x is not None:
                yield from x._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.decorator_list:
            if x is not None:
                yield from x._children()
        for x in self.keywords:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Return(stmt):
    value: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.Return(value=None if self.value is None else to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=None if node.value is None else from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Return(value=None if self.value is None else self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        if self.value is not None:
            yield from self.value()._children()

@attrs.frozen()
class Delete(stmt):
    targets: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Delete(targets=[to_builtin(x) for x in self.targets])

    @classmethod
    def _from_builtin(cls, node):
        return cls(targets=[from_builtin(x) for x in node.targets])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Delete(targets=[x._transform(node_transformer, inner_context) for x in self.targets])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.targets:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Assign(stmt):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    targets: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.Assign(value=to_builtin(self.value), targets=[to_builtin(x) for x in self.targets], type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value), targets=[from_builtin(x) for x in node.targets], type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Assign(value=self.value._transform(node_transformer, inner_context), targets=[x._transform(node_transformer, inner_context) for x in self.targets], type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()
        for x in self.targets:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class AugAssign(stmt):
    op: operator = attrs.field(validator=ProxyInstanceOfValidator(lambda: operator), converter=unwrap_underscore)
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.AugAssign(op=to_builtin(self.op), target=to_builtin(self.target), value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=from_builtin(node.op), target=from_builtin(node.target), value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = AugAssign(op=self.op._transform(node_transformer, inner_context), target=self.target._transform(node_transformer, inner_context), value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.op()._children()
        yield from self.target()._children()
        yield from self.value()._children()

@attrs.frozen()
class AnnAssign(stmt):
    annotation: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    simple: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    value: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.AnnAssign(annotation=to_builtin(self.annotation), simple=self.simple, target=to_builtin(self.target), value=None if self.value is None else to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(annotation=from_builtin(node.annotation), simple=node.simple, target=from_builtin(node.target), value=None if node.value is None else from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = AnnAssign(annotation=self.annotation._transform(node_transformer, inner_context), simple=self.simple, target=self.target._transform(node_transformer, inner_context), value=None if self.value is None else self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.annotation()._children()
        yield from self.target()._children()
        if self.value is not None:
            yield from self.value()._children()

@attrs.frozen()
class For(stmt):
    iter: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    orelse: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.For(iter=to_builtin(self.iter), target=to_builtin(self.target), body=[to_builtin(x) for x in self.body], orelse=[to_builtin(x) for x in self.orelse], type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(iter=from_builtin(node.iter), target=from_builtin(node.target), body=[from_builtin(x) for x in node.body], orelse=[from_builtin(x) for x in node.orelse], type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = For(iter=self.iter._transform(node_transformer, inner_context), target=self.target._transform(node_transformer, inner_context), body=[x._transform(node_transformer, inner_context) for x in self.body], orelse=[x._transform(node_transformer, inner_context) for x in self.orelse], type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.iter()._children()
        yield from self.target()._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.orelse:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class AsyncFor(stmt):
    iter: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    orelse: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.AsyncFor(iter=to_builtin(self.iter), target=to_builtin(self.target), body=[to_builtin(x) for x in self.body], orelse=[to_builtin(x) for x in self.orelse], type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(iter=from_builtin(node.iter), target=from_builtin(node.target), body=[from_builtin(x) for x in node.body], orelse=[from_builtin(x) for x in node.orelse], type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = AsyncFor(iter=self.iter._transform(node_transformer, inner_context), target=self.target._transform(node_transformer, inner_context), body=[x._transform(node_transformer, inner_context) for x in self.body], orelse=[x._transform(node_transformer, inner_context) for x in self.orelse], type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.iter()._children()
        yield from self.target()._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.orelse:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class While(stmt):
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    orelse: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.While(test=to_builtin(self.test), body=[to_builtin(x) for x in self.body], orelse=[to_builtin(x) for x in self.orelse])

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=from_builtin(node.test), body=[from_builtin(x) for x in node.body], orelse=[from_builtin(x) for x in node.orelse])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = While(test=self.test._transform(node_transformer, inner_context), body=[x._transform(node_transformer, inner_context) for x in self.body], orelse=[x._transform(node_transformer, inner_context) for x in self.orelse])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.test()._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.orelse:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class If(stmt):
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    orelse: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.If(test=to_builtin(self.test), body=[to_builtin(x) for x in self.body], orelse=[to_builtin(x) for x in self.orelse])

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=from_builtin(node.test), body=[from_builtin(x) for x in node.body], orelse=[from_builtin(x) for x in node.orelse])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = If(test=self.test._transform(node_transformer, inner_context), body=[x._transform(node_transformer, inner_context) for x in self.body], orelse=[x._transform(node_transformer, inner_context) for x in self.orelse])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.test()._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.orelse:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class With(stmt):
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    items: Sequence[withitem] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: withitem)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.With(body=[to_builtin(x) for x in self.body], items=[to_builtin(x) for x in self.items], type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=[from_builtin(x) for x in node.body], items=[from_builtin(x) for x in node.items], type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = With(body=[x._transform(node_transformer, inner_context) for x in self.body], items=[x._transform(node_transformer, inner_context) for x in self.items], type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.items:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class AsyncWith(stmt):
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    items: Sequence[withitem] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: withitem)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.AsyncWith(body=[to_builtin(x) for x in self.body], items=[to_builtin(x) for x in self.items], type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=[from_builtin(x) for x in node.body], items=[from_builtin(x) for x in node.items], type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = AsyncWith(body=[x._transform(node_transformer, inner_context) for x in self.body], items=[x._transform(node_transformer, inner_context) for x in self.items], type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.items:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Match(stmt):
    subject: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    cases: Sequence[match_case] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: match_case)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Match(subject=to_builtin(self.subject), cases=[to_builtin(x) for x in self.cases])

    @classmethod
    def _from_builtin(cls, node):
        return cls(subject=from_builtin(node.subject), cases=[from_builtin(x) for x in node.cases])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Match(subject=self.subject._transform(node_transformer, inner_context), cases=[x._transform(node_transformer, inner_context) for x in self.cases])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.subject()._children()
        for x in self.cases:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Raise(stmt):
    cause: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)
    exc: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.Raise(cause=None if self.cause is None else to_builtin(self.cause), exc=None if self.exc is None else to_builtin(self.exc))

    @classmethod
    def _from_builtin(cls, node):
        return cls(cause=None if node.cause is None else from_builtin(node.cause), exc=None if node.exc is None else from_builtin(node.exc))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Raise(cause=None if self.cause is None else self.cause._transform(node_transformer, inner_context), exc=None if self.exc is None else self.exc._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        if self.cause is not None:
            yield from self.cause()._children()
        if self.exc is not None:
            yield from self.exc()._children()

@attrs.frozen()
class Try(stmt):
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    finalbody: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    handlers: Sequence[excepthandler] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: excepthandler)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    orelse: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Try(body=[to_builtin(x) for x in self.body], finalbody=[to_builtin(x) for x in self.finalbody], handlers=[to_builtin(x) for x in self.handlers], orelse=[to_builtin(x) for x in self.orelse])

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=[from_builtin(x) for x in node.body], finalbody=[from_builtin(x) for x in node.finalbody], handlers=[from_builtin(x) for x in node.handlers], orelse=[from_builtin(x) for x in node.orelse])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Try(body=[x._transform(node_transformer, inner_context) for x in self.body], finalbody=[x._transform(node_transformer, inner_context) for x in self.finalbody], handlers=[x._transform(node_transformer, inner_context) for x in self.handlers], orelse=[x._transform(node_transformer, inner_context) for x in self.orelse])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._children()
        for x in self.finalbody:
            if x is not None:
                yield from x._children()
        for x in self.handlers:
            if x is not None:
                yield from x._children()
        for x in self.orelse:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Assert(stmt):
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    msg: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.Assert(test=to_builtin(self.test), msg=None if self.msg is None else to_builtin(self.msg))

    @classmethod
    def _from_builtin(cls, node):
        return cls(test=from_builtin(node.test), msg=None if node.msg is None else from_builtin(node.msg))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Assert(test=self.test._transform(node_transformer, inner_context), msg=None if self.msg is None else self.msg._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.test()._children()
        if self.msg is not None:
            yield from self.msg()._children()

@attrs.frozen()
class Import(stmt):
    names: Sequence[alias] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: alias)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Import(names=[to_builtin(x) for x in self.names])

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=[from_builtin(x) for x in node.names])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Import(names=[x._transform(node_transformer, inner_context) for x in self.names])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.names:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class ImportFrom(stmt):
    level: Optional[int] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: int)), default=None)
    module: Optional[str] = attrs.field(converter=attrs.converters.optional(convert_identifier), default=None)
    names: Sequence[alias] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: alias)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.ImportFrom(level=self.level, module=self.module, names=[to_builtin(x) for x in self.names])

    @classmethod
    def _from_builtin(cls, node):
        return cls(level=node.level, module=node.module, names=[from_builtin(x) for x in node.names])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = ImportFrom(level=self.level, module=self.module, names=[x._transform(node_transformer, inner_context) for x in self.names])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.names:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Global(stmt):
    names: Sequence[str] = attrs.field(converter=DeepIterableConverter(convert_identifier), factory=list)

    def _to_builtin(self):
        return ast.Global(names=self.names)

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node.names)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Global(names=self.names)
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Nonlocal(stmt):
    names: Sequence[str] = attrs.field(converter=DeepIterableConverter(convert_identifier), factory=list)

    def _to_builtin(self):
        return ast.Nonlocal(names=self.names)

    @classmethod
    def _from_builtin(cls, node):
        return cls(names=node.names)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Nonlocal(names=self.names)
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Expr(stmt):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.Expr(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Expr(value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()

@attrs.frozen()
class Pass(stmt):

    def _to_builtin(self):
        return ast.Pass()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Pass()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Break(stmt):

    def _to_builtin(self):
        return ast.Break()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Break()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Continue(stmt):

    def _to_builtin(self):
        return ast.Continue()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Continue()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

class expr(Node):
    pass

@attrs.frozen()
class BoolOp(expr):
    op: boolop = attrs.field(validator=ProxyInstanceOfValidator(lambda: boolop), converter=unwrap_underscore)
    values: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.BoolOp(op=to_builtin(self.op), values=[to_builtin(x) for x in self.values])

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=from_builtin(node.op), values=[from_builtin(x) for x in node.values])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = BoolOp(op=self.op._transform(node_transformer, inner_context), values=[x._transform(node_transformer, inner_context) for x in self.values])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.op()._children()
        for x in self.values:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class NamedExpr(expr):
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.NamedExpr(target=to_builtin(self.target), value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(target=from_builtin(node.target), value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = NamedExpr(target=self.target._transform(node_transformer, inner_context), value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.target()._children()
        yield from self.value()._children()

@attrs.frozen()
class BinOp(expr):
    left: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    op: operator = attrs.field(validator=ProxyInstanceOfValidator(lambda: operator), converter=unwrap_underscore)
    right: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.BinOp(left=to_builtin(self.left), op=to_builtin(self.op), right=to_builtin(self.right))

    @classmethod
    def _from_builtin(cls, node):
        return cls(left=from_builtin(node.left), op=from_builtin(node.op), right=from_builtin(node.right))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = BinOp(left=self.left._transform(node_transformer, inner_context), op=self.op._transform(node_transformer, inner_context), right=self.right._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.left()._children()
        yield from self.op()._children()
        yield from self.right()._children()

@attrs.frozen()
class UnaryOp(expr):
    op: unaryop = attrs.field(validator=ProxyInstanceOfValidator(lambda: unaryop), converter=unwrap_underscore)
    operand: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.UnaryOp(op=to_builtin(self.op), operand=to_builtin(self.operand))

    @classmethod
    def _from_builtin(cls, node):
        return cls(op=from_builtin(node.op), operand=from_builtin(node.operand))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = UnaryOp(op=self.op._transform(node_transformer, inner_context), operand=self.operand._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.op()._children()
        yield from self.operand()._children()

@attrs.frozen()
class Lambda(expr):
    args: arguments = attrs.field(validator=ProxyInstanceOfValidator(lambda: arguments), converter=unwrap_underscore)
    body: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.Lambda(args=to_builtin(self.args), body=to_builtin(self.body))

    @classmethod
    def _from_builtin(cls, node):
        return cls(args=from_builtin(node.args), body=from_builtin(node.body))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Lambda(args=self.args._transform(node_transformer, inner_context), body=self.body._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.args()._children()
        yield from self.body()._children()

@attrs.frozen()
class IfExp(expr):
    body: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    orelse: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    test: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.IfExp(body=to_builtin(self.body), orelse=to_builtin(self.orelse), test=to_builtin(self.test))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=from_builtin(node.body), orelse=from_builtin(node.orelse), test=from_builtin(node.test))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = IfExp(body=self.body._transform(node_transformer, inner_context), orelse=self.orelse._transform(node_transformer, inner_context), test=self.test._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.body()._children()
        yield from self.orelse()._children()
        yield from self.test()._children()

@attrs.frozen()
class Dict(expr):
    keys: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    values: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Dict(keys=[to_builtin(x) for x in self.keys], values=[to_builtin(x) for x in self.values])

    @classmethod
    def _from_builtin(cls, node):
        return cls(keys=[from_builtin(x) for x in node.keys], values=[from_builtin(x) for x in node.values])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Dict(keys=[x._transform(node_transformer, inner_context) for x in self.keys], values=[x._transform(node_transformer, inner_context) for x in self.values])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.keys:
            if x is not None:
                yield from x._children()
        for x in self.values:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Set(expr):
    elts: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Set(elts=[to_builtin(x) for x in self.elts])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=[from_builtin(x) for x in node.elts])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Set(elts=[x._transform(node_transformer, inner_context) for x in self.elts])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.elts:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class ListComp(expr):
    elt: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    generators: Sequence[comprehension] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: comprehension)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.ListComp(elt=to_builtin(self.elt), generators=[to_builtin(x) for x in self.generators])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=from_builtin(node.elt), generators=[from_builtin(x) for x in node.generators])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = ListComp(elt=self.elt._transform(node_transformer, inner_context), generators=[x._transform(node_transformer, inner_context) for x in self.generators])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.elt()._children()
        for x in self.generators:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class SetComp(expr):
    elt: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    generators: Sequence[comprehension] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: comprehension)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.SetComp(elt=to_builtin(self.elt), generators=[to_builtin(x) for x in self.generators])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=from_builtin(node.elt), generators=[from_builtin(x) for x in node.generators])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = SetComp(elt=self.elt._transform(node_transformer, inner_context), generators=[x._transform(node_transformer, inner_context) for x in self.generators])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.elt()._children()
        for x in self.generators:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class DictComp(expr):
    key: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    generators: Sequence[comprehension] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: comprehension)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.DictComp(key=to_builtin(self.key), value=to_builtin(self.value), generators=[to_builtin(x) for x in self.generators])

    @classmethod
    def _from_builtin(cls, node):
        return cls(key=from_builtin(node.key), value=from_builtin(node.value), generators=[from_builtin(x) for x in node.generators])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = DictComp(key=self.key._transform(node_transformer, inner_context), value=self.value._transform(node_transformer, inner_context), generators=[x._transform(node_transformer, inner_context) for x in self.generators])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.key()._children()
        yield from self.value()._children()
        for x in self.generators:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class GeneratorExp(expr):
    elt: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    generators: Sequence[comprehension] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: comprehension)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.GeneratorExp(elt=to_builtin(self.elt), generators=[to_builtin(x) for x in self.generators])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elt=from_builtin(node.elt), generators=[from_builtin(x) for x in node.generators])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = GeneratorExp(elt=self.elt._transform(node_transformer, inner_context), generators=[x._transform(node_transformer, inner_context) for x in self.generators])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.elt()._children()
        for x in self.generators:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Await(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.Await(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Await(value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()

@attrs.frozen()
class Yield(expr):
    value: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.Yield(value=None if self.value is None else to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=None if node.value is None else from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Yield(value=None if self.value is None else self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        if self.value is not None:
            yield from self.value()._children()

@attrs.frozen()
class YieldFrom(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.YieldFrom(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = YieldFrom(value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()

@attrs.frozen()
class Compare(expr):
    left: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    comparators: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    ops: Sequence[cmpop] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: cmpop)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Compare(left=to_builtin(self.left), comparators=[to_builtin(x) for x in self.comparators], ops=[to_builtin(x) for x in self.ops])

    @classmethod
    def _from_builtin(cls, node):
        return cls(left=from_builtin(node.left), comparators=[from_builtin(x) for x in node.comparators], ops=[from_builtin(x) for x in node.ops])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Compare(left=self.left._transform(node_transformer, inner_context), comparators=[x._transform(node_transformer, inner_context) for x in self.comparators], ops=[x._transform(node_transformer, inner_context) for x in self.ops])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.left()._children()
        for x in self.comparators:
            if x is not None:
                yield from x._children()
        for x in self.ops:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Call(expr):
    func: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    args: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    keywords: Sequence[keyword] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: keyword)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Call(func=to_builtin(self.func), args=[to_builtin(x) for x in self.args], keywords=[to_builtin(x) for x in self.keywords])

    @classmethod
    def _from_builtin(cls, node):
        return cls(func=from_builtin(node.func), args=[from_builtin(x) for x in node.args], keywords=[from_builtin(x) for x in node.keywords])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Call(func=self.func._transform(node_transformer, inner_context), args=[x._transform(node_transformer, inner_context) for x in self.args], keywords=[x._transform(node_transformer, inner_context) for x in self.keywords])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.func()._children()
        for x in self.args:
            if x is not None:
                yield from x._children()
        for x in self.keywords:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class FormattedValue(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    conversion: Optional[int] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: int)), default=None)
    format_spec: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.FormattedValue(value=to_builtin(self.value), conversion=self.conversion, format_spec=None if self.format_spec is None else to_builtin(self.format_spec))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value), conversion=node.conversion, format_spec=None if node.format_spec is None else from_builtin(node.format_spec))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = FormattedValue(value=self.value._transform(node_transformer, inner_context), conversion=self.conversion, format_spec=None if self.format_spec is None else self.format_spec._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()
        if self.format_spec is not None:
            yield from self.format_spec()._children()

@attrs.frozen()
class JoinedStr(expr):
    values: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.JoinedStr(values=[to_builtin(x) for x in self.values])

    @classmethod
    def _from_builtin(cls, node):
        return cls(values=[from_builtin(x) for x in node.values])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = JoinedStr(values=[x._transform(node_transformer, inner_context) for x in self.values])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.values:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Constant(expr):
    value: Any = attrs.field()
    kind: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None)

    def _to_builtin(self):
        return ast.Constant(value=self.value, kind=self.kind)

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node.value, kind=node.kind)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Constant(value=self.value, kind=self.kind)
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Attribute(expr):
    attr: str = attrs.field(converter=convert_identifier)
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.Attribute(attr=self.attr, value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(attr=node.attr, value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Attribute(attr=self.attr, value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()

@attrs.frozen()
class Subscript(expr):
    slice: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.Subscript(slice=to_builtin(self.slice), value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(slice=from_builtin(node.slice), value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Subscript(slice=self.slice._transform(node_transformer, inner_context), value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.slice()._children()
        yield from self.value()._children()

@attrs.frozen()
class Starred(expr):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.Starred(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Starred(value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()

@attrs.frozen()
class Name(expr):
    id: str = attrs.field(converter=convert_identifier)

    def _to_builtin(self):
        return ast.Name(id=self.id)

    @classmethod
    def _from_builtin(cls, node):
        return cls(id=node.id)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Name(id=self.id)
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class List(expr):
    elts: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.List(elts=[to_builtin(x) for x in self.elts])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=[from_builtin(x) for x in node.elts])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = List(elts=[x._transform(node_transformer, inner_context) for x in self.elts])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.elts:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Tuple(expr):
    elts: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.Tuple(elts=[to_builtin(x) for x in self.elts])

    @classmethod
    def _from_builtin(cls, node):
        return cls(elts=[from_builtin(x) for x in node.elts])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Tuple(elts=[x._transform(node_transformer, inner_context) for x in self.elts])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.elts:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class Slice(expr):
    lower: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)
    step: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)
    upper: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.Slice(lower=None if self.lower is None else to_builtin(self.lower), step=None if self.step is None else to_builtin(self.step), upper=None if self.upper is None else to_builtin(self.upper))

    @classmethod
    def _from_builtin(cls, node):
        return cls(lower=None if node.lower is None else from_builtin(node.lower), step=None if node.step is None else from_builtin(node.step), upper=None if node.upper is None else from_builtin(node.upper))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Slice(lower=None if self.lower is None else self.lower._transform(node_transformer, inner_context), step=None if self.step is None else self.step._transform(node_transformer, inner_context), upper=None if self.upper is None else self.upper._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        if self.lower is not None:
            yield from self.lower()._children()
        if self.step is not None:
            yield from self.step()._children()
        if self.upper is not None:
            yield from self.upper()._children()

class expr_context(Node):
    pass

@attrs.frozen()
class Load(expr_context):

    def _to_builtin(self):
        return ast.Load()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Load()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Store(expr_context):

    def _to_builtin(self):
        return ast.Store()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Store()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Del(expr_context):

    def _to_builtin(self):
        return ast.Del()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Del()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

class boolop(Node):
    pass

@attrs.frozen()
class And(boolop):

    def _to_builtin(self):
        return ast.And()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = And()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Or(boolop):

    def _to_builtin(self):
        return ast.Or()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Or()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

class operator(Node):
    pass

@attrs.frozen()
class Add(operator):

    def _to_builtin(self):
        return ast.Add()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Add()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Sub(operator):

    def _to_builtin(self):
        return ast.Sub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Sub()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Mult(operator):

    def _to_builtin(self):
        return ast.Mult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Mult()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class MatMult(operator):

    def _to_builtin(self):
        return ast.MatMult()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatMult()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Div(operator):

    def _to_builtin(self):
        return ast.Div()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Div()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Mod(operator):

    def _to_builtin(self):
        return ast.Mod()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Mod()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Pow(operator):

    def _to_builtin(self):
        return ast.Pow()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Pow()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class LShift(operator):

    def _to_builtin(self):
        return ast.LShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = LShift()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class RShift(operator):

    def _to_builtin(self):
        return ast.RShift()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = RShift()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class BitOr(operator):

    def _to_builtin(self):
        return ast.BitOr()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = BitOr()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class BitXor(operator):

    def _to_builtin(self):
        return ast.BitXor()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = BitXor()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class BitAnd(operator):

    def _to_builtin(self):
        return ast.BitAnd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = BitAnd()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class FloorDiv(operator):

    def _to_builtin(self):
        return ast.FloorDiv()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = FloorDiv()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

class unaryop(Node):
    pass

@attrs.frozen()
class Invert(unaryop):

    def _to_builtin(self):
        return ast.Invert()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Invert()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Not(unaryop):

    def _to_builtin(self):
        return ast.Not()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Not()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class UAdd(unaryop):

    def _to_builtin(self):
        return ast.UAdd()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = UAdd()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class USub(unaryop):

    def _to_builtin(self):
        return ast.USub()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = USub()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

class cmpop(Node):
    pass

@attrs.frozen()
class Eq(cmpop):

    def _to_builtin(self):
        return ast.Eq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Eq()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class NotEq(cmpop):

    def _to_builtin(self):
        return ast.NotEq()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = NotEq()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Lt(cmpop):

    def _to_builtin(self):
        return ast.Lt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Lt()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class LtE(cmpop):

    def _to_builtin(self):
        return ast.LtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = LtE()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Gt(cmpop):

    def _to_builtin(self):
        return ast.Gt()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Gt()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class GtE(cmpop):

    def _to_builtin(self):
        return ast.GtE()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = GtE()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class Is(cmpop):

    def _to_builtin(self):
        return ast.Is()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = Is()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class IsNot(cmpop):

    def _to_builtin(self):
        return ast.IsNot()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = IsNot()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class In(cmpop):

    def _to_builtin(self):
        return ast.In()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = In()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class NotIn(cmpop):

    def _to_builtin(self):
        return ast.NotIn()

    @classmethod
    def _from_builtin(cls, node):
        return cls()

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = NotIn()
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class comprehension(Node):
    is_async: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    iter: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    target: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    ifs: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.comprehension(is_async=self.is_async, iter=to_builtin(self.iter), target=to_builtin(self.target), ifs=[to_builtin(x) for x in self.ifs])

    @classmethod
    def _from_builtin(cls, node):
        return cls(is_async=node.is_async, iter=from_builtin(node.iter), target=from_builtin(node.target), ifs=[from_builtin(x) for x in node.ifs])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = comprehension(is_async=self.is_async, iter=self.iter._transform(node_transformer, inner_context), target=self.target._transform(node_transformer, inner_context), ifs=[x._transform(node_transformer, inner_context) for x in self.ifs])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.iter()._children()
        yield from self.target()._children()
        for x in self.ifs:
            if x is not None:
                yield from x._children()

class excepthandler(Node):
    pass

@attrs.frozen()
class ExceptHandler(excepthandler):
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    name: Optional[str] = attrs.field(converter=attrs.converters.optional(convert_identifier), default=None)
    type: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.ExceptHandler(body=[to_builtin(x) for x in self.body], name=self.name, type=None if self.type is None else to_builtin(self.type))

    @classmethod
    def _from_builtin(cls, node):
        return cls(body=[from_builtin(x) for x in node.body], name=node.name, type=None if node.type is None else from_builtin(node.type))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = ExceptHandler(body=[x._transform(node_transformer, inner_context) for x in self.body], name=self.name, type=None if self.type is None else self.type._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.body:
            if x is not None:
                yield from x._children()
        if self.type is not None:
            yield from self.type()._children()

@attrs.frozen()
class arguments(Node):
    args: Sequence[arg] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    defaults: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    kw_defaults: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    kwarg: Optional[arg] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: arg)), converter=attrs.converters.optional(unwrap_underscore), default=None)
    kwonlyargs: Sequence[arg] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    posonlyargs: Sequence[arg] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: arg)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    vararg: Optional[arg] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: arg)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.arguments(args=[to_builtin(x) for x in self.args], defaults=[to_builtin(x) for x in self.defaults], kw_defaults=[to_builtin(x) for x in self.kw_defaults], kwarg=None if self.kwarg is None else to_builtin(self.kwarg), kwonlyargs=[to_builtin(x) for x in self.kwonlyargs], posonlyargs=[to_builtin(x) for x in self.posonlyargs], vararg=None if self.vararg is None else to_builtin(self.vararg))

    @classmethod
    def _from_builtin(cls, node):
        return cls(args=[from_builtin(x) for x in node.args], defaults=[from_builtin(x) for x in node.defaults], kw_defaults=[from_builtin(x) for x in node.kw_defaults], kwarg=None if node.kwarg is None else from_builtin(node.kwarg), kwonlyargs=[from_builtin(x) for x in node.kwonlyargs], posonlyargs=[from_builtin(x) for x in node.posonlyargs], vararg=None if node.vararg is None else from_builtin(node.vararg))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = arguments(args=[x._transform(node_transformer, inner_context) for x in self.args], defaults=[x._transform(node_transformer, inner_context) for x in self.defaults], kw_defaults=[x._transform(node_transformer, inner_context) for x in self.kw_defaults], kwarg=None if self.kwarg is None else self.kwarg._transform(node_transformer, inner_context), kwonlyargs=[x._transform(node_transformer, inner_context) for x in self.kwonlyargs], posonlyargs=[x._transform(node_transformer, inner_context) for x in self.posonlyargs], vararg=None if self.vararg is None else self.vararg._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.args:
            if x is not None:
                yield from x._children()
        for x in self.defaults:
            if x is not None:
                yield from x._children()
        for x in self.kw_defaults:
            if x is not None:
                yield from x._children()
        if self.kwarg is not None:
            yield from self.kwarg()._children()
        for x in self.kwonlyargs:
            if x is not None:
                yield from x._children()
        for x in self.posonlyargs:
            if x is not None:
                yield from x._children()
        if self.vararg is not None:
            yield from self.vararg()._children()

@attrs.frozen()
class arg(Node):
    arg: str = attrs.field(converter=convert_identifier)
    annotation: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)
    type_comment: Optional[str] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: str)), default=None, repr=False)

    def _to_builtin(self):
        return ast.arg(arg=self.arg, annotation=None if self.annotation is None else to_builtin(self.annotation), type_comment=self.type_comment)

    @classmethod
    def _from_builtin(cls, node):
        return cls(arg=node.arg, annotation=None if node.annotation is None else from_builtin(node.annotation), type_comment=node.type_comment)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = arg(arg=self.arg, annotation=None if self.annotation is None else self.annotation._transform(node_transformer, inner_context), type_comment=self.type_comment)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        if self.annotation is not None:
            yield from self.annotation()._children()

@attrs.frozen()
class keyword(Node):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    arg: Optional[str] = attrs.field(converter=attrs.converters.optional(convert_identifier), default=None)

    def _to_builtin(self):
        return ast.keyword(value=to_builtin(self.value), arg=self.arg)

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value), arg=node.arg)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = keyword(value=self.value._transform(node_transformer, inner_context), arg=self.arg)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()

@attrs.frozen()
class alias(Node):
    name: str = attrs.field(converter=convert_identifier)
    asname: Optional[str] = attrs.field(converter=attrs.converters.optional(convert_identifier), default=None)

    def _to_builtin(self):
        return ast.alias(name=self.name, asname=self.asname)

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node.name, asname=node.asname)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = alias(name=self.name, asname=self.asname)
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class withitem(Node):
    context_expr: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    optional_vars: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.withitem(context_expr=to_builtin(self.context_expr), optional_vars=None if self.optional_vars is None else to_builtin(self.optional_vars))

    @classmethod
    def _from_builtin(cls, node):
        return cls(context_expr=from_builtin(node.context_expr), optional_vars=None if node.optional_vars is None else from_builtin(node.optional_vars))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = withitem(context_expr=self.context_expr._transform(node_transformer, inner_context), optional_vars=None if self.optional_vars is None else self.optional_vars._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.context_expr()._children()
        if self.optional_vars is not None:
            yield from self.optional_vars()._children()

@attrs.frozen()
class match_case(Node):
    pattern: pattern = attrs.field(validator=ProxyInstanceOfValidator(lambda: pattern), converter=unwrap_underscore)
    body: Sequence[stmt] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: stmt)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    guard: Optional[expr] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: expr)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.match_case(pattern=to_builtin(self.pattern), body=[to_builtin(x) for x in self.body], guard=None if self.guard is None else to_builtin(self.guard))

    @classmethod
    def _from_builtin(cls, node):
        return cls(pattern=from_builtin(node.pattern), body=[from_builtin(x) for x in node.body], guard=None if node.guard is None else from_builtin(node.guard))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = match_case(pattern=self.pattern._transform(node_transformer, inner_context), body=[x._transform(node_transformer, inner_context) for x in self.body], guard=None if self.guard is None else self.guard._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.pattern()._children()
        for x in self.body:
            if x is not None:
                yield from x._children()
        if self.guard is not None:
            yield from self.guard()._children()

class pattern(Node):
    pass

@attrs.frozen()
class MatchValue(pattern):
    value: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)

    def _to_builtin(self):
        return ast.MatchValue(value=to_builtin(self.value))

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=from_builtin(node.value))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchValue(value=self.value._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.value()._children()

@attrs.frozen()
class MatchSingleton(pattern):
    value: Any = attrs.field()

    def _to_builtin(self):
        return ast.MatchSingleton(value=self.value)

    @classmethod
    def _from_builtin(cls, node):
        return cls(value=node.value)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchSingleton(value=self.value)
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class MatchSequence(pattern):
    patterns: Sequence[pattern] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: pattern)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.MatchSequence(patterns=[to_builtin(x) for x in self.patterns])

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=[from_builtin(x) for x in node.patterns])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchSequence(patterns=[x._transform(node_transformer, inner_context) for x in self.patterns])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.patterns:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class MatchMapping(pattern):
    keys: Sequence[expr] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: expr)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    patterns: Sequence[pattern] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: pattern)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    rest: Optional[str] = attrs.field(converter=attrs.converters.optional(convert_identifier), default=None)

    def _to_builtin(self):
        return ast.MatchMapping(keys=[to_builtin(x) for x in self.keys], patterns=[to_builtin(x) for x in self.patterns], rest=self.rest)

    @classmethod
    def _from_builtin(cls, node):
        return cls(keys=[from_builtin(x) for x in node.keys], patterns=[from_builtin(x) for x in node.patterns], rest=node.rest)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchMapping(keys=[x._transform(node_transformer, inner_context) for x in self.keys], patterns=[x._transform(node_transformer, inner_context) for x in self.patterns], rest=self.rest)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.keys:
            if x is not None:
                yield from x._children()
        for x in self.patterns:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class MatchClass(pattern):
    cls: expr = attrs.field(validator=ProxyInstanceOfValidator(lambda: expr), converter=unwrap_underscore)
    kwd_attrs: Sequence[str] = attrs.field(converter=DeepIterableConverter(convert_identifier), factory=list)
    kwd_patterns: Sequence[pattern] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: pattern)), converter=DeepIterableConverter(unwrap_underscore), factory=list)
    patterns: Sequence[pattern] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: pattern)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.MatchClass(cls=to_builtin(self.cls), kwd_attrs=self.kwd_attrs, kwd_patterns=[to_builtin(x) for x in self.kwd_patterns], patterns=[to_builtin(x) for x in self.patterns])

    @classmethod
    def _from_builtin(cls, node):
        return cls(cls=from_builtin(node.cls), kwd_attrs=node.kwd_attrs, kwd_patterns=[from_builtin(x) for x in node.kwd_patterns], patterns=[from_builtin(x) for x in node.patterns])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchClass(cls=self.cls._transform(node_transformer, inner_context), kwd_attrs=self.kwd_attrs, kwd_patterns=[x._transform(node_transformer, inner_context) for x in self.kwd_patterns], patterns=[x._transform(node_transformer, inner_context) for x in self.patterns])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        yield from self.cls()._children()
        for x in self.kwd_patterns:
            if x is not None:
                yield from x._children()
        for x in self.patterns:
            if x is not None:
                yield from x._children()

@attrs.frozen()
class MatchStar(pattern):
    name: Optional[str] = attrs.field(converter=attrs.converters.optional(convert_identifier), default=None)

    def _to_builtin(self):
        return ast.MatchStar(name=self.name)

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node.name)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchStar(name=self.name)
        return node_transformer(transformed, context)

    def _children(self):
        yield self

@attrs.frozen()
class MatchAs(pattern):
    name: Optional[str] = attrs.field(converter=attrs.converters.optional(convert_identifier), default=None)
    pattern: Optional[pattern] = attrs.field(validator=attrs.validators.optional(ProxyInstanceOfValidator(lambda: pattern)), converter=attrs.converters.optional(unwrap_underscore), default=None)

    def _to_builtin(self):
        return ast.MatchAs(name=self.name, pattern=None if self.pattern is None else to_builtin(self.pattern))

    @classmethod
    def _from_builtin(cls, node):
        return cls(name=node.name, pattern=None if node.pattern is None else from_builtin(node.pattern))

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchAs(name=self.name, pattern=None if self.pattern is None else self.pattern._transform(node_transformer, inner_context))
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        if self.pattern is not None:
            yield from self.pattern()._children()

@attrs.frozen()
class MatchOr(pattern):
    patterns: Sequence[pattern] = attrs.field(validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: pattern)), converter=DeepIterableConverter(unwrap_underscore), factory=list)

    def _to_builtin(self):
        return ast.MatchOr(patterns=[to_builtin(x) for x in self.patterns])

    @classmethod
    def _from_builtin(cls, node):
        return cls(patterns=[from_builtin(x) for x in node.patterns])

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = MatchOr(patterns=[x._transform(node_transformer, inner_context) for x in self.patterns])
        return node_transformer(transformed, context)

    def _children(self):
        yield self
        for x in self.patterns:
            if x is not None:
                yield from x._children()

class type_ignore(Node):
    pass

@attrs.frozen()
class TypeIgnore(type_ignore):
    lineno: int = attrs.field(validator=ProxyInstanceOfValidator(lambda: int))
    tag: str = attrs.field(validator=ProxyInstanceOfValidator(lambda: str))

    def _to_builtin(self):
        return ast.TypeIgnore(lineno=self.lineno, tag=self.tag)

    @classmethod
    def _from_builtin(cls, node):
        return cls(lineno=node.lineno, tag=node.tag)

    def _transform(self, node_transformer, context):
        inner_context = TransformerContext(parents=[self, *context.parents])
        transformed = TypeIgnore(lineno=self.lineno, tag=self.tag)
        return node_transformer(transformed, context)

    def _children(self):
        yield self
NODES = dict(Module=Module, Interactive=Interactive, Expression=Expression, FunctionType=FunctionType, FunctionDef=FunctionDef, AsyncFunctionDef=AsyncFunctionDef, ClassDef=ClassDef, Return=Return, Delete=Delete, Assign=Assign, AugAssign=AugAssign, AnnAssign=AnnAssign, For=For, AsyncFor=AsyncFor, While=While, If=If, With=With, AsyncWith=AsyncWith, Match=Match, Raise=Raise, Try=Try, Assert=Assert, Import=Import, ImportFrom=ImportFrom, Global=Global, Nonlocal=Nonlocal, Expr=Expr, Pass=Pass, Break=Break, Continue=Continue, BoolOp=BoolOp, NamedExpr=NamedExpr, BinOp=BinOp, UnaryOp=UnaryOp, Lambda=Lambda, IfExp=IfExp, Dict=Dict, Set=Set, ListComp=ListComp, SetComp=SetComp, DictComp=DictComp, GeneratorExp=GeneratorExp, Await=Await, Yield=Yield, YieldFrom=YieldFrom, Compare=Compare, Call=Call, FormattedValue=FormattedValue, JoinedStr=JoinedStr, Constant=Constant, Attribute=Attribute, Subscript=Subscript, Starred=Starred, Name=Name, List=List, Tuple=Tuple, Slice=Slice, Load=Load, Store=Store, Del=Del, And=And, Or=Or, Add=Add, Sub=Sub, Mult=Mult, MatMult=MatMult, Div=Div, Mod=Mod, Pow=Pow, LShift=LShift, RShift=RShift, BitOr=BitOr, BitXor=BitXor, BitAnd=BitAnd, FloorDiv=FloorDiv, Invert=Invert, Not=Not, UAdd=UAdd, USub=USub, Eq=Eq, NotEq=NotEq, Lt=Lt, LtE=LtE, Gt=Gt, GtE=GtE, Is=Is, IsNot=IsNot, In=In, NotIn=NotIn, comprehension=comprehension, ExceptHandler=ExceptHandler, arguments=arguments, arg=arg, keyword=keyword, alias=alias, withitem=withitem, match_case=match_case, MatchValue=MatchValue, MatchSingleton=MatchSingleton, MatchSequence=MatchSequence, MatchMapping=MatchMapping, MatchClass=MatchClass, MatchStar=MatchStar, MatchAs=MatchAs, MatchOr=MatchOr, TypeIgnore=TypeIgnore)