import pytest

from models.Event import Event
from models.Handler import Handler
from repositories.InMemoryRepository import InMemoryRepository
from repositories.SQLiteRepository import SQLiteRepository
from services.BusService import (
    BusRepository,
    BusService,
    AlreadyExistsError,
    EmptyNameError,
    NotFoundError,
)

# TODO - split to integration tests, read more book


@pytest.fixture(params=["in-memory", "sqlite"])
def repo(request) -> BusRepository:
    if request.param == "in-memory":
        return InMemoryRepository()
    elif request.param == "sqlite":
        return SQLiteRepository(":memory:")

    return InMemoryRepository()


@pytest.fixture
def service(repo: BusRepository) -> BusService:
    return BusService(repo)


class TestEvents:
    def test_creating(self, service: BusService):
        service.create_event("TestEvent")
        assert service.get_event("TestEvent") == Event("TestEvent", [])

    def test_creating_empty_name(self, service: BusService):
        with pytest.raises(EmptyNameError):
            service.create_event("")

    def test_creating_existing(self, service: BusService):
        service.create_event("TestEvent")

        with pytest.raises(AlreadyExistsError):
            service.create_event("TestEvent")


class TestHandlers:
    def test_creating(self, service: BusService):
        service.create_handler("TestHandler", "send_email.py")
        assert service.get_handler("TestHandler") == Handler("TestHandler", "send_email.py")

    def test_creating_empty_name(self, service: BusService):
        with pytest.raises(EmptyNameError):
            service.create_handler("", "send_email.py")

    def test_creating_existing_with_predefined_action(self, service: BusService):
        service.create_handler("TestHandler", "send_email.py")

        with pytest.raises(AlreadyExistsError):
            service.create_handler("TestHandler", "send_email.py")


class TestSubscription:
    def test_subscribe(self, service: BusService):
        event = service.create_event("TestEvent")
        handler = service.create_handler("TestHandler", "send_email.py")
        service.subscribe(event.name, handler.name)

        event = service.get_event("TestEvent")

        assert event is not None
        assert event.name == "TestEvent"
        assert len(event.handlers) == 1
        assert event.handlers[0] == handler

    def test_subscribe_nonexistent_event(self, service: BusService):
        handler = service.create_handler("TestHandler", "send_email.py")

        with pytest.raises(NotFoundError):
            service.subscribe("NonExistentEvent", handler.name)

    def test_subscribe_nonexistent_handler(self, service: BusService):
        event = service.create_event("TestEvent")

        with pytest.raises(NotFoundError):
            service.subscribe(event.name, "NonExistentHandler")

    def test_subscribe_already_subscribed_handler(self, service: BusService):
        event = service.create_event("TestEvent")
        handler = service.create_handler("TestHandler", "send_email.py")
        service.subscribe(event.name, handler.name)

        with pytest.raises(AlreadyExistsError):
            service.subscribe(event.name, handler.name)


class TestPublishing:
    def test_publish_with_handlers(self, service: BusService):
        event = service.create_event("TestEvent")
        handler1 = service.create_handler("EmailHandler", "send_email.py")
        handler2 = service.create_handler("SumHandler", "sum_numbers.py")
        service.subscribe(event.name, handler1.name)
        service.subscribe(event.name, handler2.name)
        service.publish(event.name, {"data": "xyz"})
        history = service.history()

        assert len(history) == 1
        assert history[0].event_name == "TestEvent"
        assert history[0].payload == {"data": "xyz"}
        assert len(history[0].results) == 2

    def test_publishing_without_handlers(self, service: BusService):
        event = service.create_event("TestEvent")
        service.publish(event.name, {"data": "xyz"})
        history = service.history()

        assert len(history) == 1
        assert history[0].event_name == "TestEvent"
        assert history[0].payload == {"data": "xyz"}
        assert len(history[0].results) == 0
