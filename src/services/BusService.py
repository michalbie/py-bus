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


class NotFoundError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


class EmptyNameError(Exception):
    pass


class BusService:
    def __init__(self, repository: BusRepository):
        self.repository = repository

    def create_event(self, name: str) -> Event:
        existing_events = [e.name for e in self.repository.list_events()]

        if not name:
            raise EmptyNameError("Event name cannot be empty.")

        if name in existing_events:
            raise AlreadyExistsError(f"Event {name} already exists.")

        event = self.repository.create_event(name)
        return event

    def create_handler(self, name: str, action: Callable[..., Any]):
        existing_handlers = [e.name for e in self.repository.list_handlers()]

        if not name:
            raise EmptyNameError("Handler name cannot be empty.")

        if name in existing_handlers:
            raise AlreadyExistsError(f"Handler {name} already exists.")

        handler = self.repository.create_handler(name, action)
        return handler

    def publish(self, event: Event, payload: str):
        results: dict[str, Any] = defaultdict(None)

        for handler in event.handlers:
            results[handler.name] = handler.action()

        self.repository.publish(event=event, payload=payload, results=results)

    def subscribe(self, event: Event, handler: Handler):
        if handler in event.handlers:
            raise AlreadyExistsError(
                f"Handler {handler.name} is already subscribed to event {event.name}."
            )

        if event not in self.repository.list_events():
            raise NotFoundError(f"Event {event.name} does not exist.")

        self.repository.subscribe(event=event, handler=handler)

    def list_events(self):
        return self.repository.list_events()

    def list_handlers(self):
        return self.repository.list_handlers()

    def history(self):
        return self.repository.history()
