from __future__ import annotations

import ast
from typing import Callable, Optional, Sequence, Union

import attrs

from .validators import (
    DeepIterableConverter,
    ProxyInstanceOfValidator,
    convert_identifier,
    unwrap_underscore,
)

from . import utils


class Node:
    pass
