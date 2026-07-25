import os
import tomllib
from pathlib import Path

import psycopg
import pytest
from psycopg import Connection, OperationalError

config_path = Path("config.toml")
with open(config_path, "rb") as f:
    config = tomllib.load(f)

config = config["database"]

DB_URL = os.environ["DATABASE_URL"]


@pytest.fixture(scope="module")
def db_connection():
    try:
        conn = psycopg.connect(DB_URL)
        yield conn
        conn.close()
    except OperationalError as e:
        pytest.fail(f"Can't connect to database at {DB_URL}: {e}")


def test_posgres_connection_alive(db_connection: Connection):
    """
    Ping database connection
    """

    with db_connection.cursor() as cur:
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        assert result is not None
        assert result[0] == 1


def test_progres_write_permissions(db_connection: Connection):
    with db_connection.cursor() as cur:
        cur.execute("CREATE TEMP TABLE test_permissions (id INT);")
        cur.execute("INSERT INTO test_permissions VALUES (42);")
        cur.execute("SELECT id FROM test_permissions;")
        val = cur.fetchone()[0]
        assert val == 42
