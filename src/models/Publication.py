from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

STATUS_TYPES = Literal["success", "failed", "dry_run"]


@dataclass
class Publication:
    id: str
    event_name: str
    payload: dict
    timestamp: datetime
    status: Literal["success", "failed", "dry_run"]
    results: dict[str, Any]
