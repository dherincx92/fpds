import psycopg2

from .base import Target


class PostgresTarget(Target):
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    @property
    def dsn(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def connect(self, connection_factory=None):
        return psycopg2.connect(dsn=self.dsn, connection_factory=connection_factory)
