from app import CouchbaseClient
import os
from dotenv import load_dotenv
import time

load_dotenv()

db_info = {
    "host": os.getenv("DB_HOST"),
    "bucket": os.getenv("BUCKET"),
    "scope": os.getenv("SCOPE"),
    "collection": os.getenv("COLLECTION"),
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
}

cb = CouchbaseClient.create_client(*db_info.values())
time.sleep(10)
