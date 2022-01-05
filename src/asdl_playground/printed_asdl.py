[
    Type(
        mod,
        Sum(
            [
                Constructor(
                    Module,
                    [
                        Field(stmt, body, seq=True),
                        Field(type_ignore, type_ignores, seq=True),
                    ],
                ),
                Constructor(Interactive, [Field(stmt, body, seq=True)]),
                Constructor(Expression, [Field(expr, body)]),
                Constructor(
                    FunctionType,
                    [Field(expr, argtypes, seq=True), Field(expr, returns)],
                ),
            ]
        ),
    ),
    Type(
        stmt,
        Sum(
            [
                Constructor(
                    FunctionDef,
                    [
                        Field(identifier, name),
                        Field(arguments, args),
                        Field(stmt, body, seq=True),
                        Field(expr, decorator_list, seq=True),
                        Field(expr, returns, opt=True),
                        Field(string, type_comment, opt=True),
                    ],
                ),
                Constructor(
                    AsyncFunctionDef,
                    [
                        Field(identifier, name),
                        Field(arguments, args),
                        Field(stmt, body, seq=True),
                        Field(expr, decorator_list, seq=True),
                        Field(expr, returns, opt=True),
                        Field(string, type_comment, opt=True),
                    ],
                ),
                Constructor(
                    ClassDef,
                    [
                        Field(identifier, name),
                        Field(expr, bases, seq=True),
                        Field(keyword, keywords, seq=True),
                        Field(stmt, body, seq=True),
                        Field(expr, decorator_list, seq=True),
                    ],
                ),
                Constructor(Return, [Field(expr, value, opt=True)]),
                Constructor(Delete, [Field(expr, targets, seq=True)]),
                Constructor(
                    Assign,
                    [
                        Field(expr, targets, seq=True),
                        Field(expr, value),
                        Field(string, type_comment, opt=True),
                    ],
                ),
                Constructor(
                    AugAssign,
                    [Field(expr, target), Field(operator, op), Field(expr, value)],
                ),
                Constructor(
                    AnnAssign,
                    [
                        Field(expr, target),
                        Field(expr, annotation),
                        Field(expr, value, opt=True),
                        Field(int, simple),
                    ],
                ),
                Constructor(
                    For,
                    [
                        Field(expr, target),
                        Field(expr, iter),
                        Field(stmt, body, seq=True),
                        Field(stmt, orelse, seq=True),
                        Field(string, type_comment, opt=True),
                    ],
                ),
                Constructor(
                    AsyncFor,
                    [
                        Field(expr, target),
                        Field(expr, iter),
                        Field(stmt, body, seq=True),
                        Field(stmt, orelse, seq=True),
                        Field(string, type_comment, opt=True),
                    ],
                ),
                Constructor(
                    While,
                    [
                        Field(expr, test),
                        Field(stmt, body, seq=True),
                        Field(stmt, orelse, seq=True),
                    ],
                ),
                Constructor(
                    If,
                    [
                        Field(expr, test),
                        Field(stmt, body, seq=True),
                        Field(stmt, orelse, seq=True),
                    ],
                ),
                Constructor(
                    With,
                    [
                        Field(withitem, items, seq=True),
                        Field(stmt, body, seq=True),
                        Field(string, type_comment, opt=True),
                    ],
                ),
                Constructor(
                    AsyncWith,
                    [
                        Field(withitem, items, seq=True),
                        Field(stmt, body, seq=True),
                        Field(string, type_comment, opt=True),
                    ],
                ),
                Constructor(
                    Match, [Field(expr, subject), Field(match_case, cases, seq=True)]
                ),
                Constructor(
                    Raise, [Field(expr, exc, opt=True), Field(expr, cause, opt=True)]
                ),
                Constructor(
                    Try,
                    [
                        Field(stmt, body, seq=True),
                        Field(excepthandler, handlers, seq=True),
                        Field(stmt, orelse, seq=True),
                        Field(stmt, finalbody, seq=True),
                    ],
                ),
                Constructor(Assert, [Field(expr, test), Field(expr, msg, opt=True)]),
                Constructor(Import, [Field(alias, names, seq=True)]),
                Constructor(
                    ImportFrom,
                    [
                        Field(identifier, module, opt=True),
                        Field(alias, names, seq=True),
                        Field(int, level, opt=True),
                    ],
                ),
                Constructor(Global, [Field(identifier, names, seq=True)]),
                Constructor(Nonlocal, [Field(identifier, names, seq=True)]),
                Constructor(Expr, [Field(expr, value)]),
                Constructor(Pass, []),
                Constructor(Break, []),
                Constructor(Continue, []),
            ],
            [
                Field(int, lineno),
                Field(int, col_offset),
                Field(int, end_lineno, opt=True),
                Field(int, end_col_offset, opt=True),
            ],
        ),
    ),
    Type(
        expr,
        Sum(
            [
                Constructor(BoolOp, [Field(boolop, op), Field(expr, values, seq=True)]),
                Constructor(NamedExpr, [Field(expr, target), Field(expr, value)]),
                Constructor(
                    BinOp, [Field(expr, left), Field(operator, op), Field(expr, right)]
                ),
                Constructor(UnaryOp, [Field(unaryop, op), Field(expr, operand)]),
                Constructor(Lambda, [Field(arguments, args), Field(expr, body)]),
                Constructor(
                    IfExp, [Field(expr, test), Field(expr, body), Field(expr, orelse)]
                ),
                Constructor(
                    Dict, [Field(expr, keys, seq=True), Field(expr, values, seq=True)]
                ),
                Constructor(Set, [Field(expr, elts, seq=True)]),
                Constructor(
                    ListComp,
                    [Field(expr, elt), Field(comprehension, generators, seq=True)],
                ),
                Constructor(
                    SetComp,
                    [Field(expr, elt), Field(comprehension, generators, seq=True)],
                ),
                Constructor(
                    DictComp,
                    [
                        Field(expr, key),
                        Field(expr, value),
                        Field(comprehension, generators, seq=True),
                    ],
                ),
                Constructor(
                    GeneratorExp,
                    [Field(expr, elt), Field(comprehension, generators, seq=True)],
                ),
                Constructor(Await, [Field(expr, value)]),
                Constructor(Yield, [Field(expr, value, opt=True)]),
                Constructor(YieldFrom, [Field(expr, value)]),
                Constructor(
                    Compare,
                    [
                        Field(expr, left),
                        Field(cmpop, ops, seq=True),
                        Field(expr, comparators, seq=True),
                    ],
                ),
                Constructor(
                    Call,
                    [
                        Field(expr, func),
                        Field(expr, args, seq=True),
                        Field(keyword, keywords, seq=True),
                    ],
                ),
                Constructor(
                    FormattedValue,
                    [
                        Field(expr, value),
                        Field(int, conversion, opt=True),
                        Field(expr, format_spec, opt=True),
                    ],
                ),
                Constructor(JoinedStr, [Field(expr, values, seq=True)]),
                Constructor(
                    Constant, [Field(constant, value), Field(string, kind, opt=True)]
                ),
                Constructor(
                    Attribute,
                    [
                        Field(expr, value),
                        Field(identifier, attr),
                        Field(expr_context, ctx),
                    ],
                ),
                Constructor(
                    Subscript,
                    [Field(expr, value), Field(expr, slice), Field(expr_context, ctx)],
                ),
                Constructor(Starred, [Field(expr, value), Field(expr_context, ctx)]),
                Constructor(Name, [Field(identifier, id), Field(expr_context, ctx)]),
                Constructor(
                    List, [Field(expr, elts, seq=True), Field(expr_context, ctx)]
                ),
                Constructor(
                    Tuple, [Field(expr, elts, seq=True), Field(expr_context, ctx)]
                ),
                Constructor(
                    Slice,
                    [
                        Field(expr, lower, opt=True),
                        Field(expr, upper, opt=True),
                        Field(expr, step, opt=True),
                    ],
                ),
            ],
            [
                Field(int, lineno),
                Field(int, col_offset),
                Field(int, end_lineno, opt=True),
                Field(int, end_col_offset, opt=True),
            ],
        ),
    ),
    Type(
        expr_context,
        Sum([Constructor(Load, []), Constructor(Store, []), Constructor(Del, [])]),
    ),
    Type(boolop, Sum([Constructor(And, []), Constructor(Or, [])])),
    Type(
        operator,
        Sum(
            [
                Constructor(Add, []),
                Constructor(Sub, []),
                Constructor(Mult, []),
                Constructor(MatMult, []),
                Constructor(Div, []),
                Constructor(Mod, []),
                Constructor(Pow, []),
                Constructor(LShift, []),
                Constructor(RShift, []),
                Constructor(BitOr, []),
                Constructor(BitXor, []),
                Constructor(BitAnd, []),
                Constructor(FloorDiv, []),
            ]
        ),
    ),
    Type(
        unaryop,
        Sum(
            [
                Constructor(Invert, []),
                Constructor(Not, []),
                Constructor(UAdd, []),
                Constructor(USub, []),
            ]
        ),
    ),
    Type(
        cmpop,
        Sum(
            [
                Constructor(Eq, []),
                Constructor(NotEq, []),
                Constructor(Lt, []),
                Constructor(LtE, []),
                Constructor(Gt, []),
                Constructor(GtE, []),
                Constructor(Is, []),
                Constructor(IsNot, []),
                Constructor(In, []),
                Constructor(NotIn, []),
            ]
        ),
    ),
    Type(
        comprehension,
        Product(
            [
                Field(expr, target),
                Field(expr, iter),
                Field(expr, ifs, seq=True),
                Field(int, is_async),
            ]
        ),
    ),
    Type(
        excepthandler,
        Sum(
            [
                Constructor(
                    ExceptHandler,
                    [
                        Field(expr, type, opt=True),
                        Field(identifier, name, opt=True),
                        Field(stmt, body, seq=True),
                    ],
                )
            ],
            [
                Field(int, lineno),
                Field(int, col_offset),
                Field(int, end_lineno, opt=True),
                Field(int, end_col_offset, opt=True),
            ],
        ),
    ),
    Type(
        arguments,
        Product(
            [
                Field(arg, posonlyargs, seq=True),
                Field(arg, args, seq=True),
                Field(arg, vararg, opt=True),
                Field(arg, kwonlyargs, seq=True),
                Field(expr, kw_defaults, seq=True),
                Field(arg, kwarg, opt=True),
                Field(expr, defaults, seq=True),
            ]
        ),
    ),
    Type(
        arg,
        Product(
            [
                Field(identifier, arg),
                Field(expr, annotation, opt=True),
                Field(string, type_comment, opt=True),
            ],
            [
                Field(int, lineno),
                Field(int, col_offset),
                Field(int, end_lineno, opt=True),
                Field(int, end_col_offset, opt=True),
            ],
        ),
    ),
    Type(
        keyword,
        Product(
            [Field(identifier, arg, opt=True), Field(expr, value)],
            [
                Field(int, lineno),
                Field(int, col_offset),
                Field(int, end_lineno, opt=True),
                Field(int, end_col_offset, opt=True),
            ],
        ),
    ),
    Type(
        alias,
        Product(
            [Field(identifier, name), Field(identifier, asname, opt=True)],
            [
                Field(int, lineno),
                Field(int, col_offset),
                Field(int, end_lineno, opt=True),
                Field(int, end_col_offset, opt=True),
            ],
        ),
    ),
    Type(
        withitem,
        Product([Field(expr, context_expr), Field(expr, optional_vars, opt=True)]),
    ),
    Type(
        match_case,
        Product(
            [
                Field(pattern, pattern),
                Field(expr, guard, opt=True),
                Field(stmt, body, seq=True),
            ]
        ),
    ),
    Type(
        pattern,
        Sum(
            [
                Constructor(MatchValue, [Field(expr, value)]),
                Constructor(MatchSingleton, [Field(constant, value)]),
                Constructor(MatchSequence, [Field(pattern, patterns, seq=True)]),
                Constructor(
                    MatchMapping,
                    [
                        Field(expr, keys, seq=True),
                        Field(pattern, patterns, seq=True),
                        Field(identifier, rest, opt=True),
                    ],
                ),
                Constructor(
                    MatchClass,
                    [
                        Field(expr, cls),
                        Field(pattern, patterns, seq=True),
                        Field(identifier, kwd_attrs, seq=True),
                        Field(pattern, kwd_patterns, seq=True),
                    ],
                ),
                Constructor(MatchStar, [Field(identifier, name, opt=True)]),
                Constructor(
                    MatchAs,
                    [
                        Field(pattern, pattern, opt=True),
                        Field(identifier, name, opt=True),
                    ],
                ),
                Constructor(MatchOr, [Field(pattern, patterns, seq=True)]),
            ],
            [
                Field(int, lineno),
                Field(int, col_offset),
                Field(int, end_lineno),
                Field(int, end_col_offset),
            ],
        ),
    ),
    Type(
        type_ignore,
        Sum([Constructor(TypeIgnore, [Field(int, lineno), Field(string, tag)])]),
    ),
]

{
    "mod": Sum(
        [
            Constructor(
                Module,
                [
                    Field(stmt, body, seq=True),
                    Field(type_ignore, type_ignores, seq=True),
                ],
            ),
            Constructor(Interactive, [Field(stmt, body, seq=True)]),
            Constructor(Expression, [Field(expr, body)]),
            Constructor(
                FunctionType, [Field(expr, argtypes, seq=True), Field(expr, returns)]
            ),
        ]
    ),
    "stmt": Sum(
        [
            Constructor(
                FunctionDef,
                [
                    Field(identifier, name),
                    Field(arguments, args),
                    Field(stmt, body, seq=True),
                    Field(expr, decorator_list, seq=True),
                    Field(expr, returns, opt=True),
                    Field(string, type_comment, opt=True),
                ],
            ),
            Constructor(
                AsyncFunctionDef,
                [
                    Field(identifier, name),
                    Field(arguments, args),
                    Field(stmt, body, seq=True),
                    Field(expr, decorator_list, seq=True),
                    Field(expr, returns, opt=True),
                    Field(string, type_comment, opt=True),
                ],
            ),
            Constructor(
                ClassDef,
                [
                    Field(identifier, name),
                    Field(expr, bases, seq=True),
                    Field(keyword, keywords, seq=True),
                    Field(stmt, body, seq=True),
                    Field(expr, decorator_list, seq=True),
                ],
            ),
            Constructor(Return, [Field(expr, value, opt=True)]),
            Constructor(Delete, [Field(expr, targets, seq=True)]),
            Constructor(
                Assign,
                [
                    Field(expr, targets, seq=True),
                    Field(expr, value),
                    Field(string, type_comment, opt=True),
                ],
            ),
            Constructor(
                AugAssign,
                [Field(expr, target), Field(operator, op), Field(expr, value)],
            ),
            Constructor(
                AnnAssign,
                [
                    Field(expr, target),
                    Field(expr, annotation),
                    Field(expr, value, opt=True),
                    Field(int, simple),
                ],
            ),
            Constructor(
                For,
                [
                    Field(expr, target),
                    Field(expr, iter),
                    Field(stmt, body, seq=True),
                    Field(stmt, orelse, seq=True),
                    Field(string, type_comment, opt=True),
                ],
            ),
            Constructor(
                AsyncFor,
                [
                    Field(expr, target),
                    Field(expr, iter),
                    Field(stmt, body, seq=True),
                    Field(stmt, orelse, seq=True),
                    Field(string, type_comment, opt=True),
                ],
            ),
            Constructor(
                While,
                [
                    Field(expr, test),
                    Field(stmt, body, seq=True),
                    Field(stmt, orelse, seq=True),
                ],
            ),
            Constructor(
                If,
                [
                    Field(expr, test),
                    Field(stmt, body, seq=True),
                    Field(stmt, orelse, seq=True),
                ],
            ),
            Constructor(
                With,
                [
                    Field(withitem, items, seq=True),
                    Field(stmt, body, seq=True),
                    Field(string, type_comment, opt=True),
                ],
            ),
            Constructor(
                AsyncWith,
                [
                    Field(withitem, items, seq=True),
                    Field(stmt, body, seq=True),
                    Field(string, type_comment, opt=True),
                ],
            ),
            Constructor(
                Match, [Field(expr, subject), Field(match_case, cases, seq=True)]
            ),
            Constructor(
                Raise, [Field(expr, exc, opt=True), Field(expr, cause, opt=True)]
            ),
            Constructor(
                Try,
                [
                    Field(stmt, body, seq=True),
                    Field(excepthandler, handlers, seq=True),
                    Field(stmt, orelse, seq=True),
                    Field(stmt, finalbody, seq=True),
                ],
            ),
            Constructor(Assert, [Field(expr, test), Field(expr, msg, opt=True)]),
            Constructor(Import, [Field(alias, names, seq=True)]),
            Constructor(
                ImportFrom,
                [
                    Field(identifier, module, opt=True),
                    Field(alias, names, seq=True),
                    Field(int, level, opt=True),
                ],
            ),
            Constructor(Global, [Field(identifier, names, seq=True)]),
            Constructor(Nonlocal, [Field(identifier, names, seq=True)]),
            Constructor(Expr, [Field(expr, value)]),
            Constructor(Pass, []),
            Constructor(Break, []),
            Constructor(Continue, []),
        ],
        [
            Field(int, lineno),
            Field(int, col_offset),
            Field(int, end_lineno, opt=True),
            Field(int, end_col_offset, opt=True),
        ],
    ),
    "expr": Sum(
        [
            Constructor(BoolOp, [Field(boolop, op), Field(expr, values, seq=True)]),
            Constructor(NamedExpr, [Field(expr, target), Field(expr, value)]),
            Constructor(
                BinOp, [Field(expr, left), Field(operator, op), Field(expr, right)]
            ),
            Constructor(UnaryOp, [Field(unaryop, op), Field(expr, operand)]),
            Constructor(Lambda, [Field(arguments, args), Field(expr, body)]),
            Constructor(
                IfExp, [Field(expr, test), Field(expr, body), Field(expr, orelse)]
            ),
            Constructor(
                Dict, [Field(expr, keys, seq=True), Field(expr, values, seq=True)]
            ),
            Constructor(Set, [Field(expr, elts, seq=True)]),
            Constructor(
                ListComp, [Field(expr, elt), Field(comprehension, generators, seq=True)]
            ),
            Constructor(
                SetComp, [Field(expr, elt), Field(comprehension, generators, seq=True)]
            ),
            Constructor(
                DictComp,
                [
                    Field(expr, key),
                    Field(expr, value),
                    Field(comprehension, generators, seq=True),
                ],
            ),
            Constructor(
                GeneratorExp,
                [Field(expr, elt), Field(comprehension, generators, seq=True)],
            ),
            Constructor(Await, [Field(expr, value)]),
            Constructor(Yield, [Field(expr, value, opt=True)]),
            Constructor(YieldFrom, [Field(expr, value)]),
            Constructor(
                Compare,
                [
                    Field(expr, left),
                    Field(cmpop, ops, seq=True),
                    Field(expr, comparators, seq=True),
                ],
            ),
            Constructor(
                Call,
                [
                    Field(expr, func),
                    Field(expr, args, seq=True),
                    Field(keyword, keywords, seq=True),
                ],
            ),
            Constructor(
                FormattedValue,
                [
                    Field(expr, value),
                    Field(int, conversion, opt=True),
                    Field(expr, format_spec, opt=True),
                ],
            ),
            Constructor(JoinedStr, [Field(expr, values, seq=True)]),
            Constructor(
                Constant, [Field(constant, value), Field(string, kind, opt=True)]
            ),
            Constructor(
                Attribute,
                [Field(expr, value), Field(identifier, attr), Field(expr_context, ctx)],
            ),
            Constructor(
                Subscript,
                [Field(expr, value), Field(expr, slice), Field(expr_context, ctx)],
            ),
            Constructor(Starred, [Field(expr, value), Field(expr_context, ctx)]),
            Constructor(Name, [Field(identifier, id), Field(expr_context, ctx)]),
            Constructor(List, [Field(expr, elts, seq=True), Field(expr_context, ctx)]),
            Constructor(Tuple, [Field(expr, elts, seq=True), Field(expr_context, ctx)]),
            Constructor(
                Slice,
                [
                    Field(expr, lower, opt=True),
                    Field(expr, upper, opt=True),
                    Field(expr, step, opt=True),
                ],
            ),
        ],
        [
            Field(int, lineno),
            Field(int, col_offset),
            Field(int, end_lineno, opt=True),
            Field(int, end_col_offset, opt=True),
        ],
    ),
    "expr_context": Sum(
        [Constructor(Load, []), Constructor(Store, []), Constructor(Del, [])]
    ),
    "boolop": Sum([Constructor(And, []), Constructor(Or, [])]),
    "operator": Sum(
        [
            Constructor(Add, []),
            Constructor(Sub, []),
            Constructor(Mult, []),
            Constructor(MatMult, []),
            Constructor(Div, []),
            Constructor(Mod, []),
            Constructor(Pow, []),
            Constructor(LShift, []),
            Constructor(RShift, []),
            Constructor(BitOr, []),
            Constructor(BitXor, []),
            Constructor(BitAnd, []),
            Constructor(FloorDiv, []),
        ]
    ),
    "unaryop": Sum(
        [
            Constructor(Invert, []),
            Constructor(Not, []),
            Constructor(UAdd, []),
            Constructor(USub, []),
        ]
    ),
    "cmpop": Sum(
        [
            Constructor(Eq, []),
            Constructor(NotEq, []),
            Constructor(Lt, []),
            Constructor(LtE, []),
            Constructor(Gt, []),
            Constructor(GtE, []),
            Constructor(Is, []),
            Constructor(IsNot, []),
            Constructor(In, []),
            Constructor(NotIn, []),
        ]
    ),
    "comprehension": Product(
        [
            Field(expr, target),
            Field(expr, iter),
            Field(expr, ifs, seq=True),
            Field(int, is_async),
        ]
    ),
    "excepthandler": Sum(
        [
            Constructor(
                ExceptHandler,
                [
                    Field(expr, type, opt=True),
                    Field(identifier, name, opt=True),
                    Field(stmt, body, seq=True),
                ],
            )
        ],
        [
            Field(int, lineno),
            Field(int, col_offset),
            Field(int, end_lineno, opt=True),
            Field(int, end_col_offset, opt=True),
        ],
    ),
    "arguments": Product(
        [
            Field(arg, posonlyargs, seq=True),
            Field(arg, args, seq=True),
            Field(arg, vararg, opt=True),
            Field(arg, kwonlyargs, seq=True),
            Field(expr, kw_defaults, seq=True),
            Field(arg, kwarg, opt=True),
            Field(expr, defaults, seq=True),
        ]
    ),
    "arg": Product(
        [
            Field(identifier, arg),
            Field(expr, annotation, opt=True),
            Field(string, type_comment, opt=True),
        ],
        [
            Field(int, lineno),
            Field(int, col_offset),
            Field(int, end_lineno, opt=True),
            Field(int, end_col_offset, opt=True),
        ],
    ),
    "keyword": Product(
        [Field(identifier, arg, opt=True), Field(expr, value)],
        [
            Field(int, lineno),
            Field(int, col_offset),
            Field(int, end_lineno, opt=True),
            Field(int, end_col_offset, opt=True),
        ],
    ),
    "alias": Product(
        [Field(identifier, name), Field(identifier, asname, opt=True)],
        [
            Field(int, lineno),
            Field(int, col_offset),
            Field(int, end_lineno, opt=True),
            Field(int, end_col_offset, opt=True),
        ],
    ),
    "withitem": Product(
        [Field(expr, context_expr), Field(expr, optional_vars, opt=True)]
    ),
    "match_case": Product(
        [
            Field(pattern, pattern),
            Field(expr, guard, opt=True),
            Field(stmt, body, seq=True),
        ]
    ),
    "pattern": Sum(
        [
            Constructor(MatchValue, [Field(expr, value)]),
            Constructor(MatchSingleton, [Field(constant, value)]),
            Constructor(MatchSequence, [Field(pattern, patterns, seq=True)]),
            Constructor(
                MatchMapping,
                [
                    Field(expr, keys, seq=True),
                    Field(pattern, patterns, seq=True),
                    Field(identifier, rest, opt=True),
                ],
            ),
            Constructor(
                MatchClass,
                [
                    Field(expr, cls),
                    Field(pattern, patterns, seq=True),
                    Field(identifier, kwd_attrs, seq=True),
                    Field(pattern, kwd_patterns, seq=True),
                ],
            ),
            Constructor(MatchStar, [Field(identifier, name, opt=True)]),
            Constructor(
                MatchAs,
                [Field(pattern, pattern, opt=True), Field(identifier, name, opt=True)],
            ),
            Constructor(MatchOr, [Field(pattern, patterns, seq=True)]),
        ],
        [
            Field(int, lineno),
            Field(int, col_offset),
            Field(int, end_lineno),
            Field(int, end_col_offset),
        ],
    ),
    "type_ignore": Sum(
        [Constructor(TypeIgnore, [Field(int, lineno), Field(string, tag)])]
    ),
}
