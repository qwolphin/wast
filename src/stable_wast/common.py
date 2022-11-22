from typing import Sequence

import attrs


class Node:
    pass


class WrappedNode:
    pass


@attrs.define
class TransformerContext:
    parents: Sequence[Node]
    original: Node
