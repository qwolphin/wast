from pathlib import Path
from activated_wast import w
from itertools import chain


def generate_key(entry):
    # ./fragments/prefixes/meow.py -> ('prefixes', 'meow')
    return entry.relative_to(fragments_dir).with_suffix("").parts


def load_fragment(entry):
    text = entry.read_text()
    raw = w.parse(text)
    body = raw.body  # unwrap module

    assert len(body)

    # extract expressions from Expr()
    if all(isinstance(x, w.Expr) for x in body):
        body = [x.value for x in body]

    # extract single statement/expression
    if text.startswith("# single\n"):
        assert len(body) == 1
        return body[0]

    return body


fragments_dir = Path("./fragments")

fragments = {
    generate_key(x): load_fragment(x)
    for x in fragments_dir.glob("**/*.py")
    if x.is_file()
}

used_fragments = set()


def get_fragment(*args, default=...):
    key = tuple(chain.from_iterable(x.split("/") for x in args))
    used_fragments.add(key)

    if default is ...:
        return fragments[key]

    return fragments.get(key, default)


def report_unused_fragments():
    unused = set(fragments.keys()) - used_fragments

    if unused:
        print(f"The following fragments look unused: {unused}")
