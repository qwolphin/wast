import dev.wast as w

# from dev.helpers import compare
from dev.wast import _

# n = compare(w.Name("a"), "is no", w.Name("b"), "not in", w.Name("r"))
# print(n)
# print(w.unparse(n))
w.parse("lambda *r, a, a=2: 1")
