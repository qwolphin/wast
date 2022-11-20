from itertools import cycle
from typing import Literal
from abc import ABC
import attrs
from . import wast as n

class FreeUnderscore:

    def __getattr__(self, name):
        return BoundUnderscore(n.Name(id=name))

    def __call__(self, name, *attrs):
        ret = n.Name(id=name)
        for name in reversed(attrs):
            ret = n.Attribute(value=ret, attr=name)
        return BoundUnderscore(ret)

    def __getitem__(self, key):
        assert isinstance(key, (str, int, float, complex, bool, type(None), type(...))), '_[] is only for simple literals'
        return BoundUnderscore(n.Constant(key))
_ = FreeUnderscore()
_comparasion_ops = {'<': n.Lt(), '<=': n.LtE(), '>': n.Gt(), '>=': n.GtE(), '==': n.Eq(), '!=': n.NotEq(), 'is': n.Is(), 'is not': n.IsNot(), 'in': n.In(), 'not in': n.NotIn()}
OperatorString = Literal['<', '<=', '>', '>=', '==', '!=', 'is', 'is not', 'in', 'not in']

def compare(*args: OperatorString | n.expr) -> n.Compare:
    exprs = []
    operators = []
    try:
        for type_, entry in zip(cycle([n.expr, str]), args):
            if not isinstance(entry, type_):
                raise ValueError()
            if type_ is n.expr:
                exprs.append(entry)
            else:
                operators.append(_comparasion_ops[entry])
    except ValueError:
        raise Exception('Mailformed')
    assert len(exprs) >= 2
    assert len(exprs) == len(operators) + 1
    return n.Compare(left=exprs[0], ops=operators, comparators=exprs[1:])
UNSET = object()

@attrs.define(init=False)
class AbstractArg(ABC):
    name: str
    annotation: n.expr | None = None

    def _as_narg(self):
        return n.arg(self.name, self.annotation)

@attrs.define(init=False)
class AbstractDefaultArg(AbstractArg, ABC):
    default: n.expr | Literal[UNSET] = UNSET

@attrs.define
class PosOnlyArg(AbstractDefaultArg):
    pass

@attrs.define
class Arg(AbstractDefaultArg):
    pass

@attrs.define
class Args(AbstractArg):
    pass

@attrs.define
class KwOnlyArg(AbstractDefaultArg):
    pass

@attrs.define
class KwArgs(AbstractArg):
    pass

def convert_arguments(value: n.arguments | list[AbstractArg | str]):
    match value:
        case n.arguments():
            return value
        case list() | tuple():
            args_list = [Arg(x) if isinstance(x, str) else x for x in value]
            assert all((isinstance(x, AbstractArg) for x in args_list))
        case other:
            assert False
    previous = []
    ret = n.arguments()
    for a in args_list:
        match a:
            case PosOnlyArg():
                assert all((isinstance(x, PosOnlyArg) for x in previous))
                new = dict(posonlyargs=[*ret.posonlyargs, a._as_narg()])
                if a.default is UNSET:
                    assert not ret.defaults
                else:
                    new |= dict(defaults=[*ret.defaults, a.default])
            case Arg():
                assert all((isinstance(x, (PosOnlyArg, Arg)) for x in previous))
                new = dict(args=[*ret.args, a._as_narg()])
                if a.default is UNSET:
                    assert not ret.defaults
                else:
                    new |= dict(defaults=[*ret.defaults, a.default])
            case Args():
                assert all((isinstance(x, (PosOnlyArg, Arg)) for x in previous))
                new = dict(vararg=a._as_narg())
            case KwOnlyArg():
                assert all((isinstance(x, (PosOnlyArg, Arg, Args)) for x in previous))
                new = dict(args=[*ret.args, a._as_narg()])
                if a.default is UNSET:
                    assert all((x is None for x in ret.kw_defaults))
                    new |= dict(defaults=[*ret.kw_defaults, None])
                else:
                    new |= dict(defaults=[*ret.kw_defaults, a.default])
            case KwArgs():
                assert all((isinstance(x, (PosOnlyArg, Arg, Args, KwOnlyArg)) for x in previous))
                new = dict(kwarg=a._as_narg())
            case other:
                assert False
        previous.append(a)
        ret = attrs.evolve(ret, **new)
    return ret

class BoundUnderscore(object):

    def __repr__(self):
        return f'W({self.__inner__})'

    def __init__(self, inner):
        assert isinstance(inner, n.expr)
        self.__inner__ = inner

    def __getattr__(self, name):
        return BoundUnderscore(n.Attribute(value=self.__inner__, attr=name))

    def __call__(self, *args, **kwargs):
        return BoundUnderscore(n.Call(func=self.__inner__, args=args, keywords=[n.keyword(value=v, arg=k) for k, v in kwargs.items()]))

    def __getitem__(self, key):
        match key:
            case slice():
                _slice = slice(lower=key.start, upper=key.stop, step=key.step)
            case BoundUnderscore() | Node():
                _slice = key
            case any:
                raise TypeError()
        return BoundUnderscore(n.Subscript(slice=_slice, value=self.__inner__))

    def __bool__(self):
        raise Exception('Chained comparasions???')

    def _(self, *attrs):
        ret = self.__inner__
        for name in reversed(attrs):
            ret = n.Attribute(value=ret, attr=name)
        return BoundUnderscore(ret)

    def __add__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=Add(), right=other.__inner__))

    def __sub__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=Sub(), right=other.__inner__))

    def __truediv__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=Div(), right=other.__inner__))

    def __floordiv__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=FloorDiv(), right=other.__inner__))

    def __mod__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=Mod(), right=other.__inner__))

    def __mul__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=Mult(), right=other.__inner__))

    def __matmul__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=MatMult(), right=other.__inner__))

    def __pow__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=Pow(), right=other.__inner__))

    def __lshift__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=LShift(), right=other.__inner__))

    def __rshift__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=RShift(), right=other.__inner__))

    def __and__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=And(), right=other.__inner__))

    def __xor__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=BitXor(), right=other.__inner__))

    def __or__(self, other):
        return BoundUnderscore(BinOp(left=self.__inner__, op=BitOr(), right=other.__inner__))

    def __neg__(self):
        return UnaryOp(op=USub(), operand=self.__inner__)

    def __pos__(self):
        return UnaryOp(op=UAdd(), operand=self.__inner__)

    def __invert__(self):
        return UnaryOp(op=Invert(), operand=self.__inner__)

    def __lt__(self, other):
        return BoundUnderscore(Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Lt()]))

    def __le__(self, other):
        return BoundUnderscore(Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Le()]))

    def __gt__(self, other):
        return BoundUnderscore(Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Gt()]))

    def __ge__(self, other):
        return BoundUnderscore(Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Ge()]))

    def __eq__(self, other):
        return BoundUnderscore(Compare(left=self.__inner__, comparators=[other.__inner__], ops=[Eq()]))

    def __ne__(self, other):
        return BoundUnderscore(Compare(left=self.__inner__, comparators=[other.__inner__], ops=[NotEq()]))