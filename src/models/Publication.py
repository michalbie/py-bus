from dataclasses import dataclass
from datetime import datetime
from typing_extensions import Literal


@dataclass
class Publication:
    id: int
    event_name: str
    payload: dict
    timestamp: datetime
    status: Literal["success", "failed", "dry_run"]
    results: list