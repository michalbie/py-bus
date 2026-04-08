from copy import deepcopy
from typing import List

from models.Event import Event
from models.Handler import Handler
from models.Publication import Publication
from services.BusService import BusRepository


class InMemoryRepository(BusRepository):
    def __init__(self):
        self.events: dict[str, Event] = {}
        self.handlers: dict[str, Handler] = {}
        self.publications: dict[str, Publication] = {}

    def create_event(self, event: Event) -> None:
        self.events[event.name] = deepcopy(event)

    def create_handler(self, handler: Handler) -> None:
        self.handlers[handler.name] = deepcopy(handler)

    def get_event(self, name: str) -> Event | None:
        return self.events.get(name)

    def get_handler(self, name: str) -> Handler | None:
        return self.handlers.get(name)

    def publish(self, publication: Publication) -> None:
        self.publications[publication.id] = deepcopy(publication)

    def subscribe(self, event: Event, handler: Handler) -> None:
        self.events[event.name] = deepcopy(event)

    def list_events(self) -> List[Event]:
        return [event for event in self.events.values()]

    def list_handlers(self) -> List[Handler]:
        return [handler for handler in self.handlers.values()]

    def history(self) -> List[Publication]:
        return [publication for publication in self.publications.values()]
