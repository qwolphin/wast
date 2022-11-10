from activated_wast import transformer, w, _
from fragments import FRAGMENTS


@transformer(type=w.Name, include=[lambda x, c: x.id.startswith("b")])
def change_b_names(node, context):
    return w.Name(f"updated_{node.id}")


original = FRAGMENTS["example"]
new = w.transform(original, change_b_names)

print(w.unparse(original))
print("\n\n\n")
print(w.unparse(new))
