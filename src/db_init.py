import requests
import os
from dotenv import load_dotenv
import time
from requests.models import HTTPError
from requests.auth import HTTPBasicAuth

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
host = os.getenv("DB_HOST")
bucket = os.getenv("BUCKET")
scope = os.getenv("SCOPE")
collection = os.getenv("COLLECTION")

auth = HTTPBasicAuth(f"{username}", f"{password}")


def create_bucket():
    """Create the bucket on the cluster using the REST API"""
    result = requests.post(
        url=f"http://{host}:8091/pools/default/buckets",
        data={"name": bucket, "ramQuotaMB": 128},
        auth=auth,
    )
    try:
        result.raise_for_status()
    except HTTPError as e:
        print(f"Bucket may exist: {result.json()['errors']}")


# def create_scope():
#     """Create the bucket on the cluster using the REST API"""
#     result = requests.post(
#         url=f"http://{host}:8091/pools/default/buckets/{bucket}/scopes",
#         data={"name": os.getenv("SCOPE")},
#         auth=auth,
#     )
#     print(result, result.status_code, result.json())
#     try:
#         result.raise_for_status()
#     except HTTPError as e:
#         print(f"Error: {result.json()['errors']}")


def create_collection():
    """Create the bucket on the cluster using the REST API"""
    result = requests.post(
        url=f"http://{host}:8091/pools/default/buckets/{bucket}/scopes/{scope}/collections",
        data={"name": collection},
        auth=auth,
    )
    try:
        result.raise_for_status()
    except HTTPError as e:
        print(f"Collection may exist: {result.json()['errors']}")


print("Initializing DB")
create_bucket()
time.sleep(5)
create_collection()
time.sleep(5)
print("Initializing DB complete")
