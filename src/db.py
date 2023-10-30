from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from datetime import timedelta


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
        self.app = app
        self.connect()

    def connect(self):
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
            except CouchbaseException as error:
                print(f"Could not connect to cluster. Error: {error}")
                raise

            # get a reference to our bucket
            self.bucket = self.cluster.bucket(self.bucket_name)
            if not self.check_scope_exists():
                print(
                    "Inventory scope does not exist in the bucket. Ensure that you have the travel-sample bucket loaded in the cluster."
                )
                exit()

            # get a reference to our scope
            self.scope = self.bucket.scope(self.scope_name)

    def check_scope_exists(self) -> bool:
        """Check if the scope exists in the bucket"""
        try:
            scopes_in_bucket = [
                scope.name for scope in self.bucket.collections().get_all_scopes()
            ]
            return self.scope_name in scopes_in_bucket
        except Exception as e:
            print(
                "Error fetching scopes in cluster. Ensure that travel-sample bucket exists."
            )
            raise

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
