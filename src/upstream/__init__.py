from pathlib import Path
from . import asdl

file = Path(__file__).parent / "Python.asdl"
parsed = asdl.ASDLParser().parse(file.read_text())
dfns = parsed.dfns
