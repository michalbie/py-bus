from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Handler:
    name: str
    action: Callable[..., Any]
