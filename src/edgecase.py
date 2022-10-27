from dev.wast import _, parse, unparse
import dev.wast as w

tree = w.parse('x = 1 + a + b.c + d[e]')

for x in [*tree._nodes_iter()]:
    print(x)
