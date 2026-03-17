from dataclasses import dataclass, field

from models.Handler import Handler


@dataclass
class Event:
    name: str
    handlers: list[Handler] = field(default_factory=list)
