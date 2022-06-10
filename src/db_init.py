import os
import time

from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.management.collections import CollectionSpec
from couchbase.management.buckets import BucketSettings
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
host = os.getenv("DB_HOST")
bucket = os.getenv("BUCKET")
scope = os.getenv("SCOPE")
collection = os.getenv("COLLECTION")


def create_bucket(cluster):
    """Create the bucket on the cluster using the SDK"""
    try:
        # create bucket if it doesn't exist
        bucketSettings = BucketSettings(name=bucket, ram_quota_mb=256)
        cluster.buckets().create_bucket(bucketSettings)
    except Exception as e:
        print(f"Error: {e}")


def create_scope(cluster):
    """Create the scope on the cluster using the SDK"""
    try:
        bkt = cluster.bucket(bucket)
        bkt.collections().create_scope(scope)
    except Exception as e:
        print(f"NError: {e}")


def create_collection(cluster):
    """Create the collection on the cluster using the SDK"""
    try:
        colSpec = CollectionSpec(collection, scope_name=scope)
        bkt = cluster.bucket(bucket)
        bkt.collections().create_collection(colSpec)
    except Exception as e:
        print(f"MError: {e}")


def initialize_db():
    """Method to initialize Couchbase installed locally"""
    # Connection String for Local Couchbase Installation
    connection_str = "couchbase://" + host

    print("Initializing DB")
    cluster = Cluster(
        connection_str,
        ClusterOptions(PasswordAuthenticator(username, password)),
    )

    # Create Bucket
    create_bucket(cluster)
    time.sleep(5)

    # Create Scope & Collection
    create_scope(cluster)
    create_collection(cluster)
    time.sleep(5)

    print("Initializing DB complete")


# Use the following initialize_db() for Capella as it communicates with TLS.
# This example does not use certificates for authentication. In production, you should have it enabled.
# Also ensure that the bucket is created on Capella before running the application.
# def initialize_db():
#     """Method to initialize Couchbase using Capella"""
#     # Connection String for Couchbase Capella
#     connection_str = "couchbases://" + host + "?ssl=no_verify"

#     print("Initializing DB")
#     cluster = Cluster(
#         connection_str,
#         ClusterOptions(PasswordAuthenticator(username, password)),
#     )

#     # Create Scope & Collection
#     create_scope(cluster)
#     create_collection(cluster)
#     time.sleep(5)

#     print("Initializing DB complete")


if __name__ == "__main__":
    initialize_db()
