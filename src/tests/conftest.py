import pytest
import os
import sys

sys.path.append("..")

BASE = "http://127.0.0.1:8080"
BASE_URI = f"{BASE}/api/v1"


@pytest.fixture(scope="session")
def couchbase_client():
    from src.db import CouchbaseClient
    from dotenv import load_dotenv

    load_dotenv()

    conn_str = os.getenv("DB_CONN_STR")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")

    couchbase_client = CouchbaseClient()
    couchbase_client.init_app(conn_str, username, password, None)

    return couchbase_client


@pytest.fixture(scope="module")
def airport_api():
    return f"{BASE_URI}/airport"


@pytest.fixture(scope="module")
def airport_collection():
    return "airport"


@pytest.fixture(scope="module")
def airline_api():
    return f"{BASE_URI}/airline"


@pytest.fixture(scope="module")
def airline_collection():
    return "airline"


@pytest.fixture(scope="module")
def route_api():
    return f"{BASE_URI}/route"


@pytest.fixture(scope="module")
def route_collection():
    return "route"
