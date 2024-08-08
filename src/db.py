import json
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from datetime import timedelta
from couchbase.management.search import SearchIndex
from couchbase.exceptions import QueryIndexAlreadyExistsException
from couchbase.options import SearchOptions
from couchbase.search import MatchQuery, ConjunctionQuery, TermQuery
import couchbase.search as search


class CouchbaseClient(object):
    """Class to handle interactions with Couchbase cluster"""

    def __init__(self) -> None:
        self.cluster = None
        self.bucket = None
        self.scope = None
        self.app = None

    def init_app(self, conn_str: str, username: str, password: str, app):
        """Initialize connection to the Couchbase cluster"""
        self.conn_str = conn_str
        self.bucket_name = "travel-sample"
        self.scope_name = "inventory"
        self.username = username
        self.password = password
        self.index_name = "hotel_search"
        self.app = app
        self.connect()

    def connect(self) -> None:
        """Connect to the Couchbase cluster"""
        # If the connection is not established, establish it now
        if not self.cluster:
            try:
                # authentication for Couchbase cluster
                auth = PasswordAuthenticator(self.username, self.password)

                cluster_opts = ClusterOptions(auth)
                # wan_development is used to avoid latency issues while connecting to Couchbase over the internet
                cluster_opts.apply_profile("wan_development")

                # connect to the cluster
                self.cluster = Cluster(self.conn_str, cluster_opts)

                # wait until the cluster is ready for use
                self.cluster.wait_until_ready(timedelta(seconds=5))

                # get a reference to our bucket
                self.bucket = self.cluster.bucket(self.bucket_name)
            except CouchbaseException as error:
                print(f"Could not connect to cluster. \nError: {error}")
                print(
                    "Ensure that you have the travel-sample bucket loaded in the cluster."
                )
                exit()

            if not self.check_scope_exists():
                print(
                    "Inventory scope does not exist in the bucket. \nEnsure that you have the inventory scope in your travel-sample bucket."
                )
                exit()

            # get a reference to our scope
            self.scope = self.bucket.scope(self.scope_name)

            try:
                scope_index_manager = self.bucket.scope(
                    self.scope_name
                ).search_indexes()
                index_definition = json.loads(
                    open(f"{self.index_name}_index.json").read()
                )
                scope_index_manager.upsert_index(
                    SearchIndex.from_json(index_definition)
                )
            except QueryIndexAlreadyExistsException:
                print(f"Index with name '{self.index_name}' already exists")
            except Exception as e:
                print(f"Error upserting index '{self.index_name}': {e}")

    def check_scope_exists(self) -> bool:
        """Check if the scope exists in the bucket"""
        try:
            scopes_in_bucket = [
                scope.name for scope in self.bucket.collections().get_all_scopes()
            ]
            return self.scope_name in scopes_in_bucket
        except Exception as e:
            print(
                "Error fetching scopes in cluster. \nEnsure that travel-sample bucket exists."
            )
            print(e)
            exit()

    def get_document(self, collection_name: str, key: str):
        """Get document by key using KV operation"""
        return self.scope.collection(collection_name).get(key)

    def insert_document(self, collection_name: str, key: str, doc: dict):
        """Insert document using KV operation"""
        return self.scope.collection(collection_name).insert(key, doc)

    def delete_document(self, collection_name: str, key: str):
        """Delete document using KV operation"""
        return self.scope.collection(collection_name).remove(key)

    def upsert_document(self, collection_name: str, key: str, doc: dict):
        """Upsert document using KV operation"""
        return self.scope.collection(collection_name).upsert(key, doc)

    def query(self, sql_query, *options, **kwargs):
        """Query Couchbase using SQL++"""
        # options are used for positional parameters
        # kwargs are used for named parameters
        return self.scope.query(sql_query, *options, **kwargs)

    def search_by_name(self, name):
        """Perform a full-text search for hotel names using the given name"""
        try:
            searchQuery = search.SearchRequest.create(
                search.MatchQuery(name, field="name")
            )
            searchResult = self.scope.search(
                self.index_name, searchQuery, SearchOptions(limit=50, fields=["name"])
            )
            names = []
            for row in searchResult.rows():
                hotel = row.fields
                names.append(hotel.get("name", ""))
        except Exception as e:
            print("Error while performing fts search", {e})
        return names

    def filter(self, filter, limit, offset):
        """Perform a full-text search with filters and pagination"""
        try:
            conjuncts = []

            match_query_terms = ["description", "name", "title"]
            conjuncts.extend(
                [
                    MatchQuery(filter[t], field=t)
                    for t in match_query_terms
                    if t in filter
                ]
            )
            term_query_terms = ["city", "country", "state"]
            conjuncts.extend(
                [TermQuery(filter[t], field=t) for t in term_query_terms if t in filter]
            )

            if conjuncts:
                query = ConjunctionQuery(*conjuncts)
            else:
                return []

            options = SearchOptions(fields=["*"], limit=limit, skip=offset)

            result = self.scope.search(
                self.index_name, search.SearchRequest.create(query), options
            )
            hotels = []
            for row in result.rows():
                hotel = row.fields
                hotels.append(hotel)
        except Exception as e:
            print("Error while performing fts search", {e})
        return hotels
