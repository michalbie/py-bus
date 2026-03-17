import uuid
from datetime import datetime
from typing import Any, Callable, List

from models.Event import Event
from models.Handler import Handler
from models.Publication import Publication
from services.BusService import BusRepository


class InMemoryRepository(BusRepository):
    def __init__(self):
        self.events: dict[str, Event] = {}
        self.handlers: dict[str, Handler] = {}
        self.publications: dict[str, Publication] = {}

    def create_event(self, name: str) -> Event:
        event = Event(name)
        self.events[name] = event
        return event

    def create_handler(self, name: str, action: Callable[..., Any]) -> Handler:
        handler = Handler(name, action)
        self.handlers[name] = handler
        return handler

    def publish(self, event: Event, payload: str, results: dict[str, Any]):
        pub_id = str(uuid.uuid4())
        self.publications[pub_id] = Publication(
            id=pub_id,
            event_name=event.name,
            payload=payload,
            timestamp=datetime.now(),
            status="dry_run",
            results=results,
        )

    def subscribe(self, event: Event, handler: Handler):
        self.events[event.name].handlers.append(handler)

    def list_events(self) -> List[Event]:
        return [event for event in self.events.values()]

    def list_handlers(self) -> List[Handler]:
        return [handler for handler in self.handlers.values()]

    def history(self) -> List[Publication]:
        return [publication for publication in self.publications.values()]
