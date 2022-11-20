from activated_wast import _, transformer, w
from fragments import get_fragment


@transformer(type=w.Name, filter=lambda n, c: n.id.startswith("b"))
def change_b_names(node, context):
    return w.Name(f"updated_{node.id}")


@transformer(type=w.Constant)
def incr(node, context):
    return w.Constant(value=node.value + 1)


original = get_fragment("example")
new = w.transform(original, change_b_names | incr)

print(w.unparse(original))
print("\n\n\n")
print(w.unparse(new))
