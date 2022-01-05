from __future__ import annotations
import ast
import attr as attrs
from typing import Optional, Sequence, Callable
from validators import *


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


def from_built_in(node):
    if isinstance(node, ast.comprehension):
        return comprehension(**node.__dict__)
    elif isinstance(node, ast.arguments):
        return arguments(**node.__dict__)
    elif isinstance(node, ast.arg):
        return arg(**node.__dict__)
    elif isinstance(node, ast.keyword):
        return keyword(**node.__dict__)
    elif isinstance(node, ast.alias):
        return alias(**node.__dict__)
    elif isinstance(node, ast.withitem):
        return withitem(**node.__dict__)
    elif isinstance(node, ast.match_case):
        return match_case(**node.__dict__)
    elif isinstance(node, ast.Module):
        return Module(**node.__dict__)
    elif isinstance(node, ast.Interactive):
        return Interactive(**node.__dict__)
    elif isinstance(node, ast.Expression):
        return Expression(**node.__dict__)
    elif isinstance(node, ast.FunctionType):
        return FunctionType(**node.__dict__)
    elif isinstance(node, ast.FunctionDef):
        return FunctionDef(**node.__dict__)
    elif isinstance(node, ast.AsyncFunctionDef):
        return AsyncFunctionDef(**node.__dict__)
    elif isinstance(node, ast.ClassDef):
        return ClassDef(**node.__dict__)
    elif isinstance(node, ast.Return):
        return Return(**node.__dict__)
    elif isinstance(node, ast.Delete):
        return Delete(**node.__dict__)
    elif isinstance(node, ast.Assign):
        return Assign(**node.__dict__)
    elif isinstance(node, ast.AugAssign):
        return AugAssign(**node.__dict__)
    elif isinstance(node, ast.AnnAssign):
        return AnnAssign(**node.__dict__)
    elif isinstance(node, ast.For):
        return For(**node.__dict__)
    elif isinstance(node, ast.AsyncFor):
        return AsyncFor(**node.__dict__)
    elif isinstance(node, ast.While):
        return While(**node.__dict__)
    elif isinstance(node, ast.If):
        return If(**node.__dict__)
    elif isinstance(node, ast.With):
        return With(**node.__dict__)
    elif isinstance(node, ast.AsyncWith):
        return AsyncWith(**node.__dict__)
    elif isinstance(node, ast.Match):
        return Match(**node.__dict__)
    elif isinstance(node, ast.Raise):
        return Raise(**node.__dict__)
    elif isinstance(node, ast.Try):
        return Try(**node.__dict__)
    elif isinstance(node, ast.Assert):
        return Assert(**node.__dict__)
    elif isinstance(node, ast.Import):
        return Import(**node.__dict__)
    elif isinstance(node, ast.ImportFrom):
        return ImportFrom(**node.__dict__)
    elif isinstance(node, ast.Global):
        return Global(**node.__dict__)
    elif isinstance(node, ast.Nonlocal):
        return Nonlocal(**node.__dict__)
    elif isinstance(node, ast.Expr):
        return Expr(**node.__dict__)
    elif isinstance(node, ast.Pass):
        return Pass(**node.__dict__)
    elif isinstance(node, ast.Break):
        return Break(**node.__dict__)
    elif isinstance(node, ast.Continue):
        return Continue(**node.__dict__)
    elif isinstance(node, ast.BoolOp):
        return BoolOp(**node.__dict__)
    elif isinstance(node, ast.NamedExpr):
        return NamedExpr(**node.__dict__)
    elif isinstance(node, ast.BinOp):
        return BinOp(**node.__dict__)
    elif isinstance(node, ast.UnaryOp):
        return UnaryOp(**node.__dict__)
    elif isinstance(node, ast.Lambda):
        return Lambda(**node.__dict__)
    elif isinstance(node, ast.IfExp):
        return IfExp(**node.__dict__)
    elif isinstance(node, ast.Dict):
        return Dict(**node.__dict__)
    elif isinstance(node, ast.Set):
        return Set(**node.__dict__)
    elif isinstance(node, ast.ListComp):
        return ListComp(**node.__dict__)
    elif isinstance(node, ast.SetComp):
        return SetComp(**node.__dict__)
    elif isinstance(node, ast.DictComp):
        return DictComp(**node.__dict__)
    elif isinstance(node, ast.GeneratorExp):
        return GeneratorExp(**node.__dict__)
    elif isinstance(node, ast.Await):
        return Await(**node.__dict__)
    elif isinstance(node, ast.Yield):
        return Yield(**node.__dict__)
    elif isinstance(node, ast.YieldFrom):
        return YieldFrom(**node.__dict__)
    elif isinstance(node, ast.Compare):
        return Compare(**node.__dict__)
    elif isinstance(node, ast.Call):
        return Call(**node.__dict__)
    elif isinstance(node, ast.FormattedValue):
        return FormattedValue(**node.__dict__)
    elif isinstance(node, ast.JoinedStr):
        return JoinedStr(**node.__dict__)
    elif isinstance(node, ast.Constant):
        return Constant(**node.__dict__)
    elif isinstance(node, ast.Attribute):
        return Attribute(**node.__dict__)
    elif isinstance(node, ast.Subscript):
        return Subscript(**node.__dict__)
    elif isinstance(node, ast.Starred):
        return Starred(**node.__dict__)
    elif isinstance(node, ast.Name):
        return Name(**node.__dict__)
    elif isinstance(node, ast.List):
        return List(**node.__dict__)
    elif isinstance(node, ast.Tuple):
        return Tuple(**node.__dict__)
    elif isinstance(node, ast.Slice):
        return Slice(**node.__dict__)
    elif isinstance(node, ast.Load):
        return Load(**node.__dict__)
    elif isinstance(node, ast.Store):
        return Store(**node.__dict__)
    elif isinstance(node, ast.Del):
        return Del(**node.__dict__)
    elif isinstance(node, ast.And):
        return And(**node.__dict__)
    elif isinstance(node, ast.Or):
        return Or(**node.__dict__)
    elif isinstance(node, ast.Add):
        return Add(**node.__dict__)
    elif isinstance(node, ast.Sub):
        return Sub(**node.__dict__)
    elif isinstance(node, ast.Mult):
        return Mult(**node.__dict__)
    elif isinstance(node, ast.MatMult):
        return MatMult(**node.__dict__)
    elif isinstance(node, ast.Div):
        return Div(**node.__dict__)
    elif isinstance(node, ast.Mod):
        return Mod(**node.__dict__)
    elif isinstance(node, ast.Pow):
        return Pow(**node.__dict__)
    elif isinstance(node, ast.LShift):
        return LShift(**node.__dict__)
    elif isinstance(node, ast.RShift):
        return RShift(**node.__dict__)
    elif isinstance(node, ast.BitOr):
        return BitOr(**node.__dict__)
    elif isinstance(node, ast.BitXor):
        return BitXor(**node.__dict__)
    elif isinstance(node, ast.BitAnd):
        return BitAnd(**node.__dict__)
    elif isinstance(node, ast.FloorDiv):
        return FloorDiv(**node.__dict__)
    elif isinstance(node, ast.Invert):
        return Invert(**node.__dict__)
    elif isinstance(node, ast.Not):
        return Not(**node.__dict__)
    elif isinstance(node, ast.UAdd):
        return UAdd(**node.__dict__)
    elif isinstance(node, ast.USub):
        return USub(**node.__dict__)
    elif isinstance(node, ast.Eq):
        return Eq(**node.__dict__)
    elif isinstance(node, ast.NotEq):
        return NotEq(**node.__dict__)
    elif isinstance(node, ast.Lt):
        return Lt(**node.__dict__)
    elif isinstance(node, ast.LtE):
        return LtE(**node.__dict__)
    elif isinstance(node, ast.Gt):
        return Gt(**node.__dict__)
    elif isinstance(node, ast.GtE):
        return GtE(**node.__dict__)
    elif isinstance(node, ast.Is):
        return Is(**node.__dict__)
    elif isinstance(node, ast.IsNot):
        return IsNot(**node.__dict__)
    elif isinstance(node, ast.In):
        return In(**node.__dict__)
    elif isinstance(node, ast.NotIn):
        return NotIn(**node.__dict__)
    elif isinstance(node, ast.ExceptHandler):
        return ExceptHandler(**node.__dict__)
    elif isinstance(node, ast.MatchValue):
        return MatchValue(**node.__dict__)
    elif isinstance(node, ast.MatchSingleton):
        return MatchSingleton(**node.__dict__)
    elif isinstance(node, ast.MatchSequence):
        return MatchSequence(**node.__dict__)
    elif isinstance(node, ast.MatchMapping):
        return MatchMapping(**node.__dict__)
    elif isinstance(node, ast.MatchClass):
        return MatchClass(**node.__dict__)
    elif isinstance(node, ast.MatchStar):
        return MatchStar(**node.__dict__)
    elif isinstance(node, ast.MatchAs):
        return MatchAs(**node.__dict__)
    elif isinstance(node, ast.MatchOr):
        return MatchOr(**node.__dict__)
    elif isinstance(node, ast.TypeIgnore):
        return TypeIgnore(**node.__dict__)
    else:
        assert False


@attrs.s(kw_only=True)
class Mod:
    pass


@attrs.s(kw_only=True)
class Module(Mod):
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    type_ignores: Sequence[TypeIgnore] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: TypeIgnore)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Interactive(Mod):
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Expression(Mod):
    body: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class FunctionType(Mod):
    argtypes: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    returns: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class Stmt:
    pass


@attrs.s(kw_only=True)
class FunctionDef(Stmt):
    name: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    args: Arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Arguments)])
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    decorator_list: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    returns: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class AsyncFunctionDef(Stmt):
    name: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    args: Arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Arguments)])
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    decorator_list: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    returns: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class ClassDef(Stmt):
    name: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    bases: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    keywords: Sequence[Keyword] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Keyword)
        ),
        default=list,
    )
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    decorator_list: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Return(Stmt):
    value: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class Delete(Stmt):
    targets: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Assign(Stmt):
    targets: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class AugAssign(Stmt):
    target: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    op: Operator = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Operator)])
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class AnnAssign(Stmt):
    target: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    annotation: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    value: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    simple: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: int)])


@attrs.s(kw_only=True)
class For(Stmt):
    target: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    iter: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    orelse: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class AsyncFor(Stmt):
    target: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    iter: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    orelse: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class While(Stmt):
    test: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    orelse: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class If(Stmt):
    test: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    orelse: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class With(Stmt):
    items: Sequence[Withitem] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Withitem)
        ),
        default=list,
    )
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class AsyncWith(Stmt):
    items: Sequence[Withitem] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Withitem)
        ),
        default=list,
    )
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class Match(Stmt):
    subject: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    cases: Sequence[MatchCase] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: MatchCase)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Raise(Stmt):
    exc: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    cause: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class Try(Stmt):
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    handlers: Sequence[Excepthandler] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Excepthandler)
        ),
        default=list,
    )
    orelse: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )
    finalbody: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Assert(Stmt):
    test: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    msg: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class Import(Stmt):
    names: Sequence[Alias] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Alias)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class ImportFrom(Stmt):
    module: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )
    names: Sequence[Alias] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Alias)
        ),
        default=list,
    )
    level: Optional[int] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: int)]),
        default=None,
    )


@attrs.s(kw_only=True)
class Global(Stmt):
    names: Sequence[str] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            attrs.validators.and_(
                ProxyInstanceOfValidator(lambda: str), validate_identifier
            )
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Nonlocal(Stmt):
    names: Sequence[str] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            attrs.validators.and_(
                ProxyInstanceOfValidator(lambda: str), validate_identifier
            )
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Expr(Stmt):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class Pass(Stmt):
    pass


@attrs.s(kw_only=True)
class Break(Stmt):
    pass


@attrs.s(kw_only=True)
class Continue(Stmt):
    pass


@attrs.s(kw_only=True)
class Expr:
    pass


@attrs.s(kw_only=True)
class BoolOp(Expr):
    op: Boolop = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Boolop)])
    values: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class NamedExpr(Expr):
    target: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class BinOp(Expr):
    left: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    op: Operator = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Operator)])
    right: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class UnaryOp(Expr):
    op: Unaryop = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Unaryop)])
    operand: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class Lambda(Expr):
    args: Arguments = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Arguments)])
    body: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class IfExp(Expr):
    test: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    body: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    orelse: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class Dict(Expr):
    keys: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    values: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Set(Expr):
    elts: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class ListComp(Expr):
    elt: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    generators: Sequence[Comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Comprehension)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class SetComp(Expr):
    elt: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    generators: Sequence[Comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Comprehension)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class DictComp(Expr):
    key: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    generators: Sequence[Comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Comprehension)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class GeneratorExp(Expr):
    elt: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    generators: Sequence[Comprehension] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Comprehension)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Await(Expr):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class Yield(Expr):
    value: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class YieldFrom(Expr):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class Compare(Expr):
    left: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    ops: Sequence[Cmpop] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Cmpop)
        ),
        default=list,
    )
    comparators: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Call(Expr):
    func: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    args: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    keywords: Sequence[Keyword] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Keyword)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class FormattedValue(Expr):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    conversion: Optional[int] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: int)]),
        default=None,
    )
    format_spec: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class JoinedStr(Expr):
    values: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Constant(Expr):
    value: Constant = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Constant)])
    kind: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class Attribute(Expr):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    attr: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    ctx: ExprContext = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: ExprContext)]
    )


@attrs.s(kw_only=True)
class Subscript(Expr):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    slice: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    ctx: ExprContext = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: ExprContext)]
    )


@attrs.s(kw_only=True)
class Starred(Expr):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    ctx: ExprContext = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: ExprContext)]
    )


@attrs.s(kw_only=True)
class Name(Expr):
    id: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    ctx: ExprContext = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: ExprContext)]
    )


@attrs.s(kw_only=True)
class List(Expr):
    elts: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    ctx: ExprContext = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: ExprContext)]
    )


@attrs.s(kw_only=True)
class Tuple(Expr):
    elts: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    ctx: ExprContext = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: ExprContext)]
    )


@attrs.s(kw_only=True)
class Slice(Expr):
    lower: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    upper: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    step: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class ExprContext:
    pass


@attrs.s(kw_only=True)
class Load(ExprContext):
    pass


@attrs.s(kw_only=True)
class Store(ExprContext):
    pass


@attrs.s(kw_only=True)
class Del(ExprContext):
    pass


@attrs.s(kw_only=True)
class Boolop:
    pass


@attrs.s(kw_only=True)
class And(Boolop):
    pass


@attrs.s(kw_only=True)
class Or(Boolop):
    pass


@attrs.s(kw_only=True)
class Operator:
    pass


@attrs.s(kw_only=True)
class Add(Operator):
    pass


@attrs.s(kw_only=True)
class Sub(Operator):
    pass


@attrs.s(kw_only=True)
class Mult(Operator):
    pass


@attrs.s(kw_only=True)
class MatMult(Operator):
    pass


@attrs.s(kw_only=True)
class Div(Operator):
    pass


@attrs.s(kw_only=True)
class Mod(Operator):
    pass


@attrs.s(kw_only=True)
class Pow(Operator):
    pass


@attrs.s(kw_only=True)
class LShift(Operator):
    pass


@attrs.s(kw_only=True)
class RShift(Operator):
    pass


@attrs.s(kw_only=True)
class BitOr(Operator):
    pass


@attrs.s(kw_only=True)
class BitXor(Operator):
    pass


@attrs.s(kw_only=True)
class BitAnd(Operator):
    pass


@attrs.s(kw_only=True)
class FloorDiv(Operator):
    pass


@attrs.s(kw_only=True)
class Unaryop:
    pass


@attrs.s(kw_only=True)
class Invert(Unaryop):
    pass


@attrs.s(kw_only=True)
class Not(Unaryop):
    pass


@attrs.s(kw_only=True)
class UAdd(Unaryop):
    pass


@attrs.s(kw_only=True)
class USub(Unaryop):
    pass


@attrs.s(kw_only=True)
class Cmpop:
    pass


@attrs.s(kw_only=True)
class Eq(Cmpop):
    pass


@attrs.s(kw_only=True)
class NotEq(Cmpop):
    pass


@attrs.s(kw_only=True)
class Lt(Cmpop):
    pass


@attrs.s(kw_only=True)
class LtE(Cmpop):
    pass


@attrs.s(kw_only=True)
class Gt(Cmpop):
    pass


@attrs.s(kw_only=True)
class GtE(Cmpop):
    pass


@attrs.s(kw_only=True)
class Is(Cmpop):
    pass


@attrs.s(kw_only=True)
class IsNot(Cmpop):
    pass


@attrs.s(kw_only=True)
class In(Cmpop):
    pass


@attrs.s(kw_only=True)
class NotIn(Cmpop):
    pass


@attrs.s(kw_only=True)
class comprehension:
    target: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    iter: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    ifs: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    is_async: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: int)])


@attrs.s(kw_only=True)
class Excepthandler:
    pass


@attrs.s(kw_only=True)
class ExceptHandler(Excepthandler):
    type: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    name: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class arguments:
    posonlyargs: Sequence[Arg] = attrs.ib(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: Arg)),
        default=list,
    )
    args: Sequence[Arg] = attrs.ib(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: Arg)),
        default=list,
    )
    vararg: Optional[Arg] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Arg)]),
        default=None,
    )
    kwonlyargs: Sequence[Arg] = attrs.ib(
        validator=attrs.validators.deep_iterable(ProxyInstanceOfValidator(lambda: Arg)),
        default=list,
    )
    kw_defaults: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    kwarg: Optional[Arg] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Arg)]),
        default=None,
    )
    defaults: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class arg:
    arg: str = attrs.ib(
        validator=[ProxyInstanceOfValidator(lambda: str), validate_identifier]
    )
    annotation: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    type_comment: Optional[str] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: str)]),
        default=None,
    )


@attrs.s(kw_only=True)
class keyword:
    arg: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class alias:
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
class withitem:
    context_expr: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    optional_vars: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )


@attrs.s(kw_only=True)
class match_case:
    pattern: Pattern = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Pattern)])
    guard: Optional[Expr] = attrs.ib(
        validator=attrs.validators.optional([ProxyInstanceOfValidator(lambda: Expr)]),
        default=None,
    )
    body: Sequence[Stmt] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Stmt)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class Pattern:
    pass


@attrs.s(kw_only=True)
class MatchValue(Pattern):
    value: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])


@attrs.s(kw_only=True)
class MatchSingleton(Pattern):
    value: Constant = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Constant)])


@attrs.s(kw_only=True)
class MatchSequence(Pattern):
    patterns: Sequence[Pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Pattern)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class MatchMapping(Pattern):
    keys: Sequence[Expr] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Expr)
        ),
        default=list,
    )
    patterns: Sequence[Pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Pattern)
        ),
        default=list,
    )
    rest: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )


@attrs.s(kw_only=True)
class MatchClass(Pattern):
    cls: Expr = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: Expr)])
    patterns: Sequence[Pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Pattern)
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
    kwd_patterns: Sequence[Pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Pattern)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class MatchStar(Pattern):
    name: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )


@attrs.s(kw_only=True)
class MatchAs(Pattern):
    pattern: Optional[Pattern] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: Pattern)]
        ),
        default=None,
    )
    name: Optional[str] = attrs.ib(
        validator=attrs.validators.optional(
            [ProxyInstanceOfValidator(lambda: str), validate_identifier]
        ),
        default=None,
    )


@attrs.s(kw_only=True)
class MatchOr(Pattern):
    patterns: Sequence[Pattern] = attrs.ib(
        validator=attrs.validators.deep_iterable(
            ProxyInstanceOfValidator(lambda: Pattern)
        ),
        default=list,
    )


@attrs.s(kw_only=True)
class TypeIgnore:
    pass


@attrs.s(kw_only=True)
class TypeIgnore(TypeIgnore):
    lineno: int = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: int)])
    tag: str = attrs.ib(validator=[ProxyInstanceOfValidator(lambda: str)])
