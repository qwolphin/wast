from activated_wast import w, _
from fragments import get_fragment
import attrs

binops = {
    # simple
    "__add__": _.Add(),
    "__sub__": _.Sub(),
    # div
    "__truediv__": _.Div(),
    "__floordiv__": _.FloorDiv(),
    "__mod__": _.Mod(),
    # mult
    "__mul__": _.Mult(),
    "__matmul__": _.MatMult(),
    "__pow__": _.Pow(),
    # bitwise
    "__lshift__": _.LShift(),
    "__rshift__": _.RShift(),
    "__and__": _.And(),
    "__xor__": _.BitXor(),
    "__or__": _.BitOr(),
}

unops = {
    "__neg__": _.USub(),
    "__pos__": _.UAdd(),
    "__pos__": _.Invert(),
}

cmpops = {
    "__lt__": _.Lt(),
    "__le__": _.Le(),
    "__gt__": _.Gt(),
    "__ge__": _.Ge(),
    "__eq__": _.Eq(),
    "__ne__": _.NotEq(),
    "__contains__": _.In(),
}


inr = _.self.__inner__
otr = _.other.__inner__


def render_binop(dunder_name, op):
    ret = _.BoundUnderscore(_.BinOp(left=inr, op=op, right=otr))
    return w.FunctionDef(
        name=dunder_name,
        args=w.arguments(
            args=[
                w.arg(arg="self"),
                w.arg(arg="other"),
            ],
        ),
        body=[w.Return(ret)],
    )


def render_unop(dunder_name, op):
    ret = _.UnaryOp(op=op, operand=inr)
    return w.FunctionDef(
        name=dunder_name,
        args=w.arguments(
            args=[
                w.arg(arg="self"),
            ],
        ),
        body=[w.Return(ret)],
    )


def render_cmpop(dunder_name, op):
    ret = _.BoundUnderscore(
        _.Compare(
            left=inr,
            comparators=w.List([otr]),
            ops=w.List([op]),
        )
    )
    return w.FunctionDef(
        name=dunder_name,
        args=w.arguments(
            args=[
                w.arg(arg="self"),
                w.arg(arg="other"),
            ],
        ),
        body=[w.Return(ret)],
    )


c_def = get_fragment("BoundUnderscore")
body = [
    *c_def.body,
    *(render_binop(k, v) for k, v in binops.items()),
    *(render_unop(k, v) for k, v in unops.items()),
    *(render_cmpop(k, v) for k, v in cmpops.items()),
]

rendered = attrs.evolve(c_def, body=body)
