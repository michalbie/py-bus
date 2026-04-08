import contextlib
import json
from datetime import datetime
from typing import List
import sqlite3

from models.Event import Event
from models.Handler import Handler
from models.Publication import Publication
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

    def create_event(self, event: Event) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO events (name) VALUES (?)",
                (event.name,),
            )

    def create_handler(self, handler: Handler) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO handlers (name, action) VALUES (?, ?)",
                (handler.name, handler.action),
            )

    def get_event(self, name: str) -> Event | None:
        with self.conn:
            with contextlib.closing(
                self.conn.execute(
                    "SELECT e.name, h.name, h.action FROM events e LEFT JOIN subscriptions s ON e.name = s.event_name LEFT JOIN handlers h ON s.handler_name = h.name WHERE e.name = ?",
                    (name,),
                )
            ) as cursor:
                rows = cursor.fetchall()
                if not rows:
                    return None

                event_name = rows[0][0]
                handlers = [Handler(row[1], row[2]) for row in rows if row[1]]
                return Event(event_name, handlers)

    def get_handler(self, name: str) -> Handler | None:
        with self.conn:
            with contextlib.closing(
                self.conn.execute(
                    "SELECT name, action FROM handlers WHERE name = ?",
                    (name,),
                )
            ) as cursor:
                row = cursor.fetchone()
                if not row:
                    return None

                return Handler(row[0], row[1])

    def publish(self, publication: Publication) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO publications (id, event_name, payload, timestamp, status, results)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    publication.id,
                    publication.event_name,
                    json.dumps(publication.payload),
                    publication.timestamp.isoformat(),
                    publication.status,
                    json.dumps(publication.results),
                ),
            )

    def subscribe(self, event: Event, handler: Handler) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO subscriptions (event_name, handler_name) VALUES (?, ?)",
                (event.name, handler.name),
            )

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
