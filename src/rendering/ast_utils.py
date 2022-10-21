import ast


def mk_attr_s(**kwargs):
    return ast.Call(
        func=mk_aa("attrs", "s"),
        args=[],
        keywords=[ast.keyword(arg=k, value=v) for k, v in kwargs.items()],
    )


def mk_attr_ib(**kwargs):
    return ast.Call(
        func=mk_aa("attrs", "ib"),
        args=[],
        keywords=[ast.keyword(arg=k, value=v) for k, v in kwargs.items()],
    )


def mk_io_validator(val):
    return ast.Call(
        func=mk_aa("ProxyInstanceOfValidator"),
        args=[
            ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[],
                ),
                body=val,
            )
        ],
        keywords=[],
    )


def mk_opt_validator(*args):
    return ast.Call(
        func=mk_aa("attrs", "validators", "optional"),
        args=args,
        keywords=[],
    )


def mk_seq_validator(*args):
    if len(args) > 1:
        and_ed = ast.Call(
            func=mk_aa("attrs", "validators", "and_"),
            args=args,
            keywords=[],
        )
    else:
        and_ed = args[0]
    return ast.Call(
        func=mk_aa("attrs", "validators", "deep_iterable"),
        args=[and_ed],
        keywords=[],
    )


def mk_classvar_type(inner):
    return ast.Subscript(
        value=ast.Name("ClassVar"),
        slice=ast.Index(inner),
    )


def mk_optional_type(inner):
    return ast.Subscript(
        value=ast.Name("Optional"),
        slice=ast.Index(inner),
    )


def mk_literal_type(*values):
    return ast.Subscript(
        value=ast.Name("Literal"),
        slice=ast.Index(ast.Tuple([ast.Constant(x) for x in values])),
    )


def mk_seq_type(inner):
    return ast.Subscript(
        value=ast.Name("Sequence"),
        slice=ast.Index(inner),
    )


def mk_union_type(*inner):
    return ast.Subscript(
        value=ast.Name("Union"),
        slice=ast.Index(value=ast.Tuple(inner)),
    )


def mk_mapping_type(*inner):
    return ast.Subscript(
        value=ast.Name("Mapping"),
        slice=ast.Index(value=ast.Tuple(inner)),
    )


def mk_typed_dict(name, fields, total, base="TypedDict"):
    assignments = [
        ast.AnnAssign(
            target=ast.Name(x.python_name),
            annotation=x.annotation,
            value=None,
            simple=True,
        )
        for x in fields
    ]

    return ast.ClassDef(
        decorator_list=[],
        bases=[ast.Name(base)],
        keywords=[ast.keyword(arg="total", value=ast.Constant(total))],
        name=name,
        body=assignments,
    )


def mk_aa(*attributes):
    *other, our = attributes

    if not other:
        return ast.Name(our)

    return ast.Attribute(value=mk_aa(*other), attr=our)
