from activated_wast import _, w, mk_transformer, get_fragment

binops = {
    # simple
    "__add__": _.w.Add(),
    "__sub__": _.w.Sub(),
    # div
    "__truediv__": _.w.Div(),
    "__floordiv__": _.w.FloorDiv(),
    "__mod__": _.w.Mod(),
    # mult
    "__mul__": _.w.Mult(),
    "__matmul__": _.w.MatMult(),
    "__pow__": _.w.Pow(),
    # bitwise
    "__lshift__": _.w.LShift(),
    "__rshift__": _.w.RShift(),
    "__and__": _.w.And(),
    "__xor__": _.w.BitXor(),
    "__or__": _.w.BitOr(),
}

unops = {
    "__neg__": _.w.USub(),
    "__pos__": _.w.UAdd(),
    "__invert__": _.w.Invert(),
}

cmpops = {
    # < <=
    "__lt__": _.w.Lt(),
    "__le__": _.w.Le(),
    # > >=
    "__gt__": _.w.Gt(),
    "__ge__": _.w.Ge(),
    # = !=
    "__eq__": _.w.Eq(),
    "__ne__": _.w.NotEq(),
}


inr = _.self._("__inner__")
otr = _.other._("__inner__")


def render_binop(dunder_name, op):
    ret = _.w.BoundUnderscore(_.w.BinOp(left=inr, op=op, right=otr))
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
    ret = _.w.UnaryOp(op=op, operand=inr)
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
    ret = _.w.BoundUnderscore(
        _.w.Compare(
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

@mk_transformer(filter=lambda n, c: n == w.Expr(w.Name('___operator_methods')))
def inject_methods(n, c):
    return [
        *(render_binop(k, v) for k, v in binops.items()),
        *(render_unop(k, v) for k, v in unops.items()),
        *(render_cmpop(k, v) for k, v in cmpops.items()),
    ]

dirty_tree = get_fragment('helpers')
tree = inject_methods.transform(dirty_tree)
