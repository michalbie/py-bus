from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal


@dataclass
class Publication:
    id: int
    event_name: str
    payload: dict
    timestamp: datetime
    status: Literal["success", "failed", "dry_run"]
    results: dict[str, Any]
