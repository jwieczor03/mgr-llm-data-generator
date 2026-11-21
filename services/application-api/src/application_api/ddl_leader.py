"""A fenced coordinator generation bound to its advisory-lock connection."""
import threading
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session


class LeaderRetired(Exception):
    pass


class LeaderDatabase:
    def __init__(self, connection, lock_key):
        self.connection = connection
        self.lock_key = lock_key
        self.lock = threading.RLock()
        self.retired = False
        self.driver = connection.connection.dbapi_connection
        self.pid = self.driver.info.backend_pid

    def retire(self):
        with self.lock:
            self.retired = True

    @contextmanager
    def session(self):
        with self.lock:
            if self.retired or self.connection.closed or self.connection.invalidated:
                self.retired = True
                raise LeaderRetired()
            try:
                if self.connection.connection.dbapi_connection is not self.driver:
                    self.retired = True
                    raise LeaderRetired()
                with self.connection.begin():
                    owns = self.connection.execute(text("""SELECT EXISTS (
                        SELECT 1 FROM pg_locks WHERE pid=:pid AND locktype='advisory' AND granted
                        AND classid=0 AND objid=:key AND objsubid=1)"""),
                        {"pid": self.pid, "key": self.lock_key}).scalar_one()
                    if not owns:
                        self.retired = True
                        raise LeaderRetired()
                    with Session(bind=self.connection, join_transaction_mode="rollback_only") as session:
                        yield session
                        session.commit()
            except DBAPIError:
                self.retired = True
                raise

    def heartbeat(self):
        with self.session() as session:
            session.execute(text("SELECT 1"))
