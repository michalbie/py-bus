from abc import ABC, abstractmethod
from typing import List

from models.Event import Event
from models.Handler import Handler
from models.Publication import Publication
from exceptions import AlreadyExistsError, EmptyNameError, NotFoundError


class BusRepository(ABC):
    @abstractmethod
    def create_event(self, event: Event) -> None: ...

    @abstractmethod
    def create_handler(self, handler: Handler) -> None: ...

    @abstractmethod
    def get_event(self, name: str) -> Event | None: ...

    @abstractmethod
    def get_handler(self, name: str) -> Handler | None: ...

    @abstractmethod
    def publish(self, publication: Publication) -> None: ...

    @abstractmethod
    def subscribe(self, event: Event, handler: Handler) -> None: ...

    @abstractmethod
    def list_events(self) -> List[Event]: ...

    @abstractmethod
    def list_handlers(self) -> List[Handler]: ...

    @abstractmethod
    def history(self) -> List[Publication]: ...


class BusService:
    def __init__(self, repository: BusRepository):
        self.repository = repository

    def create_event(self, name: str) -> Event:
        if not name:
            raise EmptyNameError("Event name cannot be empty.")

        if self.repository.get_event(name):
            raise AlreadyExistsError(f"Event {name} already exists.")

        event = Event(name)
        self.repository.create_event(event)
        return event

    def create_handler(self, name: str, action: str):
        if not name:
            raise EmptyNameError("Handler name cannot be empty.")

        if self.repository.get_handler(name):
            raise AlreadyExistsError(f"Handler {name} already exists.")

        handler = Handler(name, action)
        self.repository.create_handler(handler)
        return handler

    def get_event(self, name: str) -> Event | None:
        return self.repository.get_event(name)

    def get_handler(self, name: str) -> Handler | None:
        return self.repository.get_handler(name)

    def publish(self, event_name: str, payload: dict) -> Publication:
        event = self.repository.get_event(event_name)

        if not event:
            raise NotFoundError("Event doesn't exist")

        publication = Publication(event_name=event.name, payload=payload)

        # Call handlers and collect results
        for handler in event.handlers:
            print(handler.action)
            publication.results[handler.name] = [True]

        for result in publication.results.values():
            if not result:
                publication.status = "failed"
                break

        self.repository.publish(publication)
        return publication

    def subscribe(self, event_name: str, handler_name: str) -> Event:
        event = self.repository.get_event(event_name)
        handler = self.repository.get_handler(handler_name)

        if event is None:
            raise NotFoundError(f"Event {event_name} does not exist.")

        if handler is None:
            raise NotFoundError(f"Handler {handler_name} does not exist.")

        event.subscribe(handler)
        self.repository.subscribe(event=event, handler=handler)
        return event

    def list_events(self):
        return self.repository.list_events()

    def list_handlers(self):
        return self.repository.list_handlers()

    def history(self):
        return self.repository.history()
