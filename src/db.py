import os
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from datetime import timedelta
from dotenv import load_dotenv


class CouchbaseClient(object):
    """Class to handle interactions with Couchbase"""

    def __init__(
        self, host: str, username: str, password: str, is_capella: bool
    ) -> None:
        self.host = host
        self.bucket_name = "travel-sample"
        self.scope_name = "inventory"
        self.capella = is_capella
        self.username = username
        self.password = password

    def connect(self):
        if self.capella:
            conn_string = f"couchbases://{self.host}"
        else:
            conn_string = f"couchbase://{self.host}"

        try:
            # authentication for Couchbase cluster
            auth = PasswordAuthenticator(self.username, self.password)

            cluster_opts = ClusterOptions(auth)
            # wan_development is used to avoid latency issues while connecting to Couchbase over the internet
            cluster_opts.apply_profile("wan_development")

            # connect to the cluster
            self._cluster = Cluster(conn_string, cluster_opts)

            # wait until the cluster is ready for use
            self._cluster.wait_until_ready(timedelta(seconds=5))
        except CouchbaseException as error:
            print(f"Could not connect to cluster. Error: {error}")
            raise

        # get a reference to our bucket
        self._bucket = self._cluster.bucket(self.bucket_name)
        if not self.check_scope_exists():
            print(
                "Inventory scope does not exist in the bucket. Ensure that you have the travel-sample bucket loaded in the cluster."
            )
            exit()

        # get a reference to our scope
        self._scope = self._bucket.scope(self.scope_name)

    def check_scope_exists(self) -> bool:
        try:
            scopes_in_bucket = [
                scope.name for scope in self._bucket.collections().get_all_scopes()
            ]
            return self.scope_name in scopes_in_bucket
        except Exception as e:
            print(
                "Error fetching scopes in cluster. Ensure that travel-sample bucket exists."
            )
            raise

    def get_document(self, collection_name: str, key: str):
        return self._scope.collection(collection_name).get(key)

    def insert_document(self, collection_name: str, key: str, doc: dict):
        return self._scope.collection(collection_name).insert(key, doc)

    def delete_document(self, collection_name: str, key: str):
        return self._scope.collection(collection_name).remove(key)

    def upsert_document(self, collection_name: str, key: str, doc: dict):
        return self._scope.collection(collection_name).upsert(key, doc)

    def query(self, sql_query, *options, **kwargs):
        # options are used for positional parameters
        # kwargs are used for named parameters
        return self._scope.query(sql_query, *options, **kwargs)
