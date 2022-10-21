import wast, ast
from pathlib import Path

text = Path('wast.py').read_text()
v=wast.node_to_wast(ast.parse(text))

print(wast.unparse(v))
