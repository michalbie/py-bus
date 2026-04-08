from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal
import uuid

STATUS_TYPES = Literal["success", "failed"]


@dataclass
class Publication:
    event_name: str
    payload: dict
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    status: STATUS_TYPES = "success"
    results: dict[str, Any] = field(default_factory=dict)
