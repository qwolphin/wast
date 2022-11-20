import attrs

from typing import Sequence


class Node:
    pass


class WrappedNode:
    pass


@attrs.define
class TransformerContext:
    parents: Sequence[Node]
    original: Node
