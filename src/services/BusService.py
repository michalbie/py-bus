from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, List

from models.Event import Event
from models.Handler import Handler
from models.Publication import Publication


class BusRepository(ABC):
    @abstractmethod
    def create_event(self, name: str) -> Event: ...

    @abstractmethod
    def create_handler(self, name: str, action: Callable[..., Any]) -> Handler: ...

    @abstractmethod
    def publish(self, event: Event, payload: str, results: dict[str, Any]): ...

    @abstractmethod
    def subscribe(self, event: Event, handler: Handler): ...

    @abstractmethod
    def list_events(self) -> List[Event]: ...

    @abstractmethod
    def list_handlers(self) -> List[Handler]: ...

    @abstractmethod
    def history(self) -> List[Publication]: ...


class EventAlreadyExistsError(Exception):
    pass


class HandlerAlreadyExistsError(Exception):
    pass


class BusService:
    def __init__(self, repository: BusRepository):
        self.repository = repository

    def create_event(self, name: str) -> Event:
        existing_events = [e.name for e in self.repository.list_events()]

        if name not in existing_events:
            event = self.repository.create_event(name)
        else:
            raise EventAlreadyExistsError(f"Event {name} already exists.")

        return event

    def create_handler(self, name: str, action: Callable[..., Any]):
        existing_handlers = [e.name for e in self.repository.list_handlers()]

        if name not in existing_handlers:
            event = self.repository.create_handler(name, action)
        else:
            raise HandlerAlreadyExistsError(f"Handler {name} already exists.")

        return event

    def publish(self, event: Event, payload: str):
        results: dict[str, Any] = defaultdict(None)

        for handler in event.handlers:
            results[handler.name] = handler.action()

        self.repository.publish(event=event, payload=payload, results=results)

    def subscribe(self, event: Event, handler: Handler):
        self.repository.subscribe(event=event, handler=handler)

    def list_events(self):
        return self.repository.list_events()

    def list_handlers(self):
        return self.repository.list_handlers()

    def history(self):
        return self.repository.history()
