"""Unit tests for CouchbaseClient search error propagation.

These tests need no running cluster: they replace the scope with a stub
whose ``search`` raises, and check that the route layer (which maps
exceptions to HTTP 500) receives the original Couchbase error.
"""

import pytest
from couchbase.exceptions import CouchbaseException

from src.db import CouchbaseClient


def _raise():
    raise CouchbaseException(message="search index unavailable")


class _FailingScope:
    """Fails when the search request is issued."""

    def search(self, *args, **kwargs):
        _raise()


class _LazyFailingResult:
    def rows(self):
        _raise()
        yield  # pragma: no cover - makes this a generator like the SDK's


class _LazyFailingScope:
    """Fails while streaming rows, as the SDK does for a missing index."""

    def search(self, *args, **kwargs):
        return _LazyFailingResult()


@pytest.fixture(params=[_FailingScope, _LazyFailingScope])
def client_with_failing_search(request):
    client = CouchbaseClient()
    client.scope = request.param()
    client.index_name = "hotel_search"
    return client


def test_search_by_name_propagates_couchbase_error(client_with_failing_search):
    with pytest.raises(CouchbaseException, match="search index unavailable"):
        client_with_failing_search.search_by_name("KCL")


def test_filter_propagates_couchbase_error(client_with_failing_search):
    with pytest.raises(CouchbaseException, match="search index unavailable"):
        client_with_failing_search.filter({"city": "Santa Margarita"}, 10, 0)


def test_filter_without_search_fields_returns_empty_list():
    client = CouchbaseClient()
    assert client.filter({}, 10, 0) == []
