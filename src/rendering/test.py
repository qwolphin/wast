import ast
import dev.wast as wast
from pathlib import Path

text = Path('stable/wast.py').read_text()
v=wast.node_to_wast(ast.parse(text))

print(wast.unparse(v))
