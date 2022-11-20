import ast

from activated_wast import _, w

builder_test = [
    (_.a + _.b, "a + b"),
]

for tree, text in builder_test:
    assert w.unparse(tree._) == text
