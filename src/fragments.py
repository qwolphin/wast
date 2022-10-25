from pathlib import Path
from activated_wast import w


def load_fragment(entry):
    text = entry.read_text()
    raw = w.parse(text)
    body = raw.body  # unwrap module

    assert len(body)

    # extract expressions from Expr()
    if all(isinstance(x, w.Expr) for x in body):
        body = [x.value for x in body]

    # extract single statement/expression
    if text.startswith('# single\n'):
        assert len(body) == 1
        return body[0]

    return body


fragments_dir = Path("./fragments")

FRAGMENTS = {x.stem: load_fragment(x) for x in fragments_dir.iterdir() if x.is_file()}
