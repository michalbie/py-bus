from models.Handler import Handler


class TestHandler:
    def test_handler_creation(self):
        handler = Handler(name="test_handler", action="send_email.py")
        assert handler.name == "test_handler"
        assert handler.action == "send_email.py"
