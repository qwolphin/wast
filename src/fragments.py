from pathlib import Path
import ast


def load_fragment(entry):
    text = entry.read_text()
    raw = ast.parse(text)
    body = raw.body

    if len(body) == 0:
        raise ValueError(
            f"Fragment {entry.stem} is empty\n\nFull path {entry.resolve(strict=True)}"
        )

    # extract expressions from statements
    if all(x.__class__.__name__ == "Expr" for x in body):
        body = [x.value for x in body]

    # extract single statement/expression
    if len(body) == 1:
        return body[0]

    return body


fragments_dir = Path("./fragments")

FRAGMENTS = {x.stem: load_fragment(x) for x in fragments_dir.iterdir() if x.is_file()}
