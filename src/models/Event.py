from dataclasses import dataclass, field

from exceptions import AlreadyExistsError
from models.Handler import Handler


@dataclass
class Event:
    name: str
    handlers: list[Handler] = field(default_factory=list)

    def subscribe(self, handler: Handler) -> None:
        if handler in self.handlers:
            raise AlreadyExistsError(
                f"Handler {handler.name} is already subscribed to event {self.name}."
            )

        self.handlers.append(handler)
