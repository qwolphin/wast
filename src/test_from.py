import ast, result
from pathlib import Path

tree = ast.parse(Path("render.py").read_text())
w_tree = result.WastTransformer().visit(tree)
w2_tree = result.WastTransformer().visit(ast.parse(Path("render.py").read_text()))
print(w_tree)
assert w_tree == w2_tree
