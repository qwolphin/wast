from activated_wast import _, n

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
    "__invert__": _.Invert(),
}

cmpops = {
    # < <=
    "__lt__": _.Lt(),
    "__le__": _.Le(),
    # > >=
    "__gt__": _.Gt(),
    "__ge__": _.Ge(),
    # = !=
    "__eq__": _.Eq(),
    "__ne__": _.NotEq(),
}


inr = _.self._("__inner__")
otr = _.other._("__inner__")


def render_binop(dunder_name, op):
    ret = _.BoundUnderscore(_.BinOp(left=inr, op=op, right=otr))
    return n.FunctionDef(
        name=dunder_name,
        args=n.arguments(
            args=[
                n.arg(arg="self"),
                n.arg(arg="other"),
            ],
        ),
        body=[n.Return(ret)],
    )


def render_unop(dunder_name, op):
    ret = _.UnaryOp(op=op, operand=inr)
    return n.FunctionDef(
        name=dunder_name,
        args=n.arguments(
            args=[
                n.arg(arg="self"),
            ],
        ),
        body=[n.Return(ret)],
    )


def render_cmpop(dunder_name, op):
    ret = _.BoundUnderscore(
        _.Compare(
            left=inr,
            comparators=n.List([otr]),
            ops=n.List([op]),
        )
    )
    return n.FunctionDef(
        name=dunder_name,
        args=n.arguments(
            args=[
                n.arg(arg="self"),
                n.arg(arg="other"),
            ],
        ),
        body=[n.Return(ret)],
    )


methods = [
    *(render_binop(k, v) for k, v in binops.items()),
    *(render_unop(k, v) for k, v in unops.items()),
    *(render_cmpop(k, v) for k, v in cmpops.items()),
]
