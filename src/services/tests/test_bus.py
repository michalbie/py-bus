import pytest

from models.Event import Event
from models.Handler import Handler
from repositories.InMemoryRepository import InMemoryRepository
from services.BusService import (
    BusRepository,
    BusService,
    EventAlreadyExistsError,
    HandlerAlreadyExistsError,
)


@pytest.fixture
def repo() -> BusRepository:
    repo: BusRepository = InMemoryRepository()
    return repo


@pytest.fixture
def service(repo: BusRepository) -> BusService:
    return BusService(repo)


# TODO - Try empty strings, None etc. for every test


class TestEvents:
    def test_creating(self, service: BusService):
        service.create_event("TestEvent")
        assert service.list_events() == [Event("TestEvent", [])]

    def test_creating_existing(self, service: BusService):
        service.create_event("TestEvent")

        with pytest.raises(EventAlreadyExistsError):
            service.create_event("TestEvent")


class TestHandlers:
    def some_func(self):
        pass

    def test_creating(self, service: BusService):
        service.create_handler("TestHandler", self.some_func)
        assert service.list_handlers() == [Handler("TestHandler", self.some_func)]

    def test_creating_existing_with_predefined_action(self, service: BusService):
        service.create_handler("TestHandler", self.some_func)

        with pytest.raises(HandlerAlreadyExistsError):
            service.create_handler("TestHandler", self.some_func)

    def test_creating_existing_with_different_action(self, service: BusService):
        service.create_handler("TestHandler", self.some_func)

        with pytest.raises(HandlerAlreadyExistsError):
            service.create_handler("TestHandler", lambda: print("different action"))


class TestBus:
    def test_subscribe(self, service: BusService):
        event = service.create_event("TestEvent")
        handler = service.repository.create_handler("TestHandler", lambda x: x)
        service.subscribe(event, handler)

        events_list = service.list_events()
        assert (
            events_list[0].name == "TestEvent"
            and len(events_list[0].handlers) == 1
            and events_list[0].handlers[0] == handler
        )

    def test_publish_with_handlers(self, service: BusService):
        def send_reminder_email():
            print("We are reminding you about...")
            return True

        def add_two_numbers(x, y):
            return x + y

        event = service.create_event("TestEvent")
        handler1 = service.repository.create_handler(
            "EmailHandler", send_reminder_email
        )
        handler2 = service.repository.create_handler(
            "SumHandler", lambda: add_two_numbers(1, 2)
        )
        service.subscribe(event, handler1)
        service.subscribe(event, handler2)
        service.publish(event, "{data: 'xyz'}")
        history = service.history()

        assert len(history) == 1
        assert history[0].event_name == "TestEvent"
        assert history[0].payload == "{data: 'xyz'}"
        assert history[0].status == "dry_run"
        assert history[0].results == {"EmailHandler": True, "SumHandler": 3}

    def test_publishing_without_handlers(self, service: BusService):
        event = service.create_event("TestEvent")
        service.publish(event, "{data: 'xyz'}")
        history = service.history()

        assert len(history) == 1
        assert history[0].event_name == "TestEvent"
        assert history[0].payload == "{data: 'xyz'}"
        assert history[0].status == "dry_run"
