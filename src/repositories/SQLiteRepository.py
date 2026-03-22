import contextlib
import json
import uuid
from datetime import datetime
from typing import Any, List
import sqlite3

from models.Event import Event
from models.Handler import Handler
from models.Publication import STATUS_TYPES, Publication
from services.BusService import BusRepository


class SQLiteRepository(BusRepository):
    def __init__(self, db_path: str = "bus.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    name TEXT PRIMARY KEY
                )
            """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS handlers (
                    name TEXT PRIMARY KEY,
                    action TEXT
                )
            """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS publications (
                    id TEXT PRIMARY KEY,
                    event_name TEXT,
                    payload TEXT,
                    timestamp TEXT,
                    status TEXT,
                    results TEXT
                )
            """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    event_name TEXT,
                    handler_name TEXT,
                    PRIMARY KEY (event_name, handler_name)
                )
            """
            )

    def create_event(self, name: str) -> Event:
        event = Event(name)
        with self.conn:
            self.conn.execute(
                "INSERT INTO events (name) VALUES (?)",
                (name,),
            )
        return event

    def create_handler(self, name: str, action: str) -> Handler:
        handler = Handler(name, action)
        with self.conn:
            self.conn.execute(
                "INSERT INTO handlers (name, action) VALUES (?, ?)",
                (name, action),
            )
        return handler

    def publish(
        self, event: Event, payload: dict, status: STATUS_TYPES, results: dict[str, Any]
    ) -> Publication:
        pub_id = str(uuid.uuid4())
        publication = Publication(
            id=pub_id,
            event_name=event.name,
            payload=payload,
            timestamp=datetime.now(),
            status=status,
            results=results,
        )
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO publications (id, event_name, payload, timestamp, status, results)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    pub_id,
                    event.name,
                    json.dumps(payload),
                    datetime.now().isoformat(),
                    status,
                    json.dumps(results),
                ),
            )
        return publication

    def subscribe(self, event: Event, handler: Handler) -> Event:
        with self.conn:
            self.conn.execute(
                "INSERT INTO subscriptions (event_name, handler_name) VALUES (?, ?) RETURNING *",
                (event.name, handler.name),
            )

        return Event(name=event.name, handlers=[*event.handlers, handler])

    def list_events(self) -> List[Event]:
        with self.conn:
            with contextlib.closing(
                self.conn.execute("""
                    SELECT e.name, h.name, h.action FROM events e
                    LEFT JOIN subscriptions s ON e.name = s.event_name
                    LEFT JOIN handlers h ON s.handler_name = h.name
                """)
            ) as cursor:
                events_dict = {}
                for row in cursor.fetchall():
                    event_name, handler_name, handler_action = row
                    if event_name not in events_dict:
                        events_dict[event_name] = Event(event_name)
                    if handler_name:
                        events_dict[event_name].handlers.append(
                            Handler(handler_name, handler_action)
                        )

                return list(events_dict.values())

    def list_handlers(self) -> List[Handler]:
        with self.conn:
            with contextlib.closing(
                self.conn.execute("SELECT name, action FROM handlers")
            ) as cursor:
                return [Handler(row[0], row[1]) for row in cursor.fetchall()]

    def history(self) -> List[Publication]:
        with self.conn:
            with contextlib.closing(
                self.conn.execute(
                    "SELECT id, event_name, payload, timestamp, status, results FROM publications"
                )
            ) as cursor:
                return [
                    Publication(
                        id=id,
                        event_name=event_name,
                        payload=json.loads(payload),
                        timestamp=datetime.fromisoformat(timestamp),
                        status=status,
                        results=json.loads(results),
                    )
                    for id, event_name, payload, timestamp, status, results in cursor.fetchall()
                ]
