from models.Event import Event
from models.Handler import Handler
from models.Publication import Publication
import pytest
from repositories.InMemoryRepository import InMemoryRepository
from repositories.SQLiteRepository import SQLiteRepository
from services.BusService import BusRepository


@pytest.fixture(params=["in-memory", "sqlite"])
def repo(request) -> BusRepository:
    if request.param == "in-memory":
        return InMemoryRepository()
    elif request.param == "sqlite":
        return SQLiteRepository(":memory:")

    return InMemoryRepository()


class TestRepository:
    def test_create_event(self, repo: BusRepository):
        event = Event(name="TestEvent")
        repo.create_event(event)
        assert repo.get_event("TestEvent") == event

    def test_create_handler(self, repo: BusRepository):
        handler = Handler(name="TestHandler", action="send_email.py")
        repo.create_handler(handler)
        assert repo.get_handler("TestHandler") == handler

    def test_subscribe(self, repo: BusRepository):
        event = Event(name="TestEvent")
        handler = Handler(name="TestHandler", action="send_email.py")

        repo.create_event(event)
        repo.create_handler(handler)
        repo.subscribe(event, handler)

        event = repo.get_event("TestEvent")

        assert getattr(event, "handlers", []) == [handler]

    def test_publish(self, repo: BusRepository):
        event = Event(name="TestEvent")
        handler1 = Handler(name="Handler1", action="send_email.py")
        handler2 = Handler(name="Handler2", action="log_event.py")

        repo.create_event(event)
        repo.create_handler(handler1)
        repo.create_handler(handler2)
        repo.subscribe(event, handler1)
        repo.subscribe(event, handler2)

        publication = Publication(event_name=event.name, payload={"data": "xyz"})

        repo.publish(publication)

        history = repo.history()

        assert len(history) == 1
        assert history[0].event_name == "TestEvent"
        assert history[0].payload == {"data": "xyz"}

    def test_list_events(self, repo: BusRepository):
        event1 = Event(name="Event1")
        event2 = Event(name="Event2")

        repo.create_event(event1)
        repo.create_event(event2)

        events = repo.list_events()

        assert len(events) == 2
        assert event1 in events
        assert event2 in events

    def test_list_handlers(self, repo: BusRepository):
        handler1 = Handler(name="Handler1", action="send_email.py")
        handler2 = Handler(name="Handler2", action="log_event.py")

        repo.create_handler(handler1)
        repo.create_handler(handler2)

        handlers = repo.list_handlers()

        assert len(handlers) == 2
        assert handler1 in handlers
        assert handler2 in handlers

    def test_get_nonexistent_event(self, repo: BusRepository):
        assert repo.get_event("NonExistentEvent") is None
