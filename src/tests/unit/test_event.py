from exceptions import AlreadyExistsError
from models.Event import Event
from models.Handler import Handler
import pytest


class TestEvent:
    def test_event_creation(self):
        event = Event(name="test_event")
        assert event.name == "test_event"
        assert event.handlers == []

    def test_event_subscription(self):
        event = Event(name="test_event")
        handler = Handler(name="test_handler", action="send_email.py")
        event.subscribe(handler)
        assert handler in event.handlers

    def test_event_subscription_duplicate(self):
        event = Event(name="test_event")
        handler = Handler(name="test_handler", action="send_email.py")
        event.subscribe(handler)

        with pytest.raises(AlreadyExistsError):
            event.subscribe(handler)
