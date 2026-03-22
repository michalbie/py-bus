import typer

from services.BusService import BusService
from repositories.SQLiteRepository import SQLiteRepository

repository = SQLiteRepository()
service = BusService(repository)
app = typer.Typer()


def main():
    print("Welcome to the event bus system!")


@app.command()
def create_event(name: str):
    """Creates a new event."""
    service.create_event(name)
    print(f"Event {name} created successfully.")


@app.command()
def create_handler(name: str, action: str):
    """Creates a new handler."""
    service.create_handler(name, action)
    print(f"Handler {name} with action {action} created successfully.")


@app.command()
def subscribe(event_name: str, handler_name: str):
    """Subscribes a handler to an event."""
    events = service.list_events()
    handlers = service.list_handlers()

    event = next((e for e in events if e.name == event_name), None)
    handler = next((h for h in handlers if h.name == handler_name), None)

    if not event:
        print(f"Event {event_name} not found.")
        return

    if not handler:
        print(f"Handler {handler_name} not found.")
        return

    service.subscribe(event=event, handler=handler)
    print(f"Handler {handler_name} subscribed to event {event_name} successfully.")


@app.command()
def publish(event_name: str, payload: str):
    """Publishes an event with a payload and status."""
    events = service.list_events()
    event = next((e for e in events if e.name == event_name), None)

    if not event:
        print(f"Event {event_name} not found.")
        return

    service.publish(event=event, payload={"data": payload})
    print(f"Event {event_name} published successfully with payload: {payload}.")


@app.command()
def list_events():
    """Lists all events."""
    events = service.list_events()
    if not events:
        print("No events found.")
        return

    print("Events:")
    for event in events:
        print(f"- {event.name}")


@app.command()
def list_handlers():
    """Lists all handlers."""
    handlers = service.list_handlers()
    if not handlers:
        print("No handlers found.")
        return

    print("Handlers:")
    for handler in handlers:
        print(f"- {handler.name} (action: {handler.action})")


@app.command()
def history():
    """Shows the history of published events."""
    history = service.history()
    if not history:
        print("No history found.")
        return

    print("History of published events:")
    for record in history:
        print(
            f"- Event: {record.event_name}, Payload: {record.payload}, Status: {record.status}, Results: {record.results}"
        )


if __name__ == "__main__":
    app()
