import warnings

from pathlib import Path
from activated_wast import w


def generate_name(entry):
    # ./fragments/prefixes/meow.py -> prefixes/meow
    return str(entry.relative_to(fragments_dir).with_suffix(""))


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


class LoggingDict(dict):
    def __init__(self, *args, **kwargs):
        self.accessed_keys = set()
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        self.accessed_keys.add(key)
        return super().__getitem__(key)


FRAGMENTS = LoggingDict(
    {
        generate_name(x): load_fragment(x)
        for x in fragments_dir.glob("**/*.py")
        if x.is_file()
    }
)


def report_unused_fragments():
    unused = set(FRAGMENTS.keys()) - FRAGMENTS.accessed_keys

    if unused:
        warnings.warn(f"The following fragments appear to be unused: {unused}")
