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
        assert service.list_events() == [Event("TestEvent", [])]

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
        assert service.list_handlers() == [Handler("TestHandler", "send_email.py")]

    def test_creating_empty_name(self, service: BusService):
        with pytest.raises(EmptyNameError):
            service.create_handler("", "send_email.py")

    def test_creating_existing_with_predefined_action(self, service: BusService):
        service.create_handler("TestHandler", "send_email.py")

        with pytest.raises(AlreadyExistsError):
            service.create_handler("TestHandler", "send_email.py")


class TestBus:
    def test_subscribe(self, service: BusService):
        event = service.create_event("TestEvent")
        handler = service.repository.create_handler("TestHandler", "send_email.py")
        service.subscribe(event, handler)
        events_list = service.list_events()

        assert events_list[0].name == "TestEvent"
        assert len(events_list[0].handlers) == 1
        assert events_list[0].handlers[0] == handler

    def test_subscribe_nonexistent_event(self, service: BusService):
        handler = service.repository.create_handler("TestHandler", "send_email.py")
        unpopulated_event = Event("NonExistentEvent")
        with pytest.raises(NotFoundError):
            service.subscribe(unpopulated_event, handler)

    def test_subscribe_already_subscribed_handler(self, service: BusService):
        event = service.create_event("TestEvent")
        handler = service.repository.create_handler("TestHandler", "send_email.py")
        event = service.subscribe(event, handler)

        with pytest.raises(AlreadyExistsError):
            service.subscribe(event, handler)

    def test_publish_with_handlers(self, service: BusService):
        event = service.create_event("TestEvent")
        handler1 = service.repository.create_handler("EmailHandler", "send_email.py")
        handler2 = service.repository.create_handler("SumHandler", "sum_numbers.py")
        event = service.subscribe(event, handler1)
        event = service.subscribe(event, handler2)
        service.publish(event, {"data": "xyz"})
        history = service.history()

        assert len(history) == 1
        assert history[0].event_name == "TestEvent"
        assert history[0].payload == {"data": "xyz"}

    def test_publishing_without_handlers(self, service: BusService):
        event = service.create_event("TestEvent")
        service.publish(event, {"data": "xyz"})
        history = service.history()

        assert len(history) == 1
        assert history[0].event_name == "TestEvent"
        assert history[0].payload == {"data": "xyz"}
        assert len(history[0].results) == 0
