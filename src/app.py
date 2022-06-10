"""
python -m pip install -r requirements.txt

export FLASK_APP=src/app && \
export FLASK_ENV=development

NOTE:  make sure to change into the src 
    directory before running flask
python db_init,py && flask run
"""
import os
import uuid
from codecs import decode
from datetime import datetime
from multiprocessing import Process

import bcrypt

# setup couchbase
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.diagnostics import PingState
from couchbase.exceptions import (
    CouchbaseException,
    DocumentExistsException,
    DocumentNotFoundException,
)
from couchbase.options import ClusterOptions
from dotenv import load_dotenv

# setup flask
from flask import Flask, jsonify, render_template, request
from flask_restx import Api, Resource, fields


class CouchbaseClient(object):
    def __init__(self, host, bucket, scope, collection, username, pw):
        self.host = host
        self.bucket_name = bucket
        self.collection_name = collection
        self.scope_name = scope
        self.username = username
        self.password = pw

    def connect(self, **kwargs):
        # note: kwargs would be how one could pass in
        #       more info for client config

        conn_str = f"couchbase://{self.host}"

        try:
            cluster_opts = ClusterOptions(
                authenticator=PasswordAuthenticator(self.username, self.password)
            )

            self._cluster = Cluster(conn_str, cluster_opts, **kwargs)
        except CouchbaseException as error:
            print(f"Could not connect to cluster. Error: {error}")
            raise

        self._bucket = self._cluster.bucket(self.bucket_name)
        self._collection = self._bucket.scope(self.scope_name).collection(
            self.collection_name
        )

        try:
            # create index if it doesn't exist
            createIndexProfile = f"CREATE PRIMARY INDEX default_profile_index ON {self.bucket_name}.{self.scope_name}.{self.collection_name}"
            createIndex = f"CREATE PRIMARY INDEX ON {self.bucket_name}"

            self._cluster.query(createIndexProfile).execute()
            self._cluster.query(createIndex).execute()
        except CouchbaseException as e:
            print("Index already exists")
        except Exception as e:
            print(f"Error: {type(e)}{e}")

    # Note: To connect with Couchbase Capella, use the following connect() instead of the one above as it communicates with TLS.
    # Also ensure that the bucket is created on Capella before running the application.

    # def connect(self, **kwargs):
    #     # note: kwargs would be how one could pass in
    #     #       more info for client config

    #     conn_str = f"couchbases://{self.host}"

    #     try:
    #         cluster_opts = ClusterOptions(
    #             authenticator=PasswordAuthenticator(self.username, self.password)
    #         )

    #         self._cluster = Cluster(conn_str, cluster_opts, **kwargs)
    #     except CouchbaseException as error:
    #         print(f"Could not connect to cluster. Error: {error}")
    #         raise

    #     self._bucket = self._cluster.bucket(self.bucket_name)
    #     self._collection = self._bucket.scope(self.scope_name).collection(
    #         self.collection_name
    #     )

    #     try:
    #         # create index if it doesn't exist
    #         createIndexProfile = f"CREATE PRIMARY INDEX default_profile_index ON {self.bucket_name}.{self.scope_name}.{self.collection_name}"
    #         createIndex = f"CREATE PRIMARY INDEX ON {self.bucket_name}"

    #         self._cluster.query(createIndexProfile).execute()
    #         self._cluster.query(createIndex).execute()
    #     except CouchbaseException as e:
    #         print("Index already exists")
    #     except Exception as e:
    #         print(f"Error: {e}")

    def ping(self):
        try:
            # check the health of cluster services
            # if couchbase version >= 3.0.10:
            # else use self._bucket.ping()
            result = self._cluster.ping()
            for _, reports in result.endpoints.items():
                for report in reports:
                    if not report.state == PingState.OK:
                        return False
            return True
        except AttributeError:
            # if the _cluster attr doesn't exist, neither does the client
            return False

    def get(self, key):
        return self._collection.get(key)

    def insert(self, key, doc):
        return self._collection.insert(key, doc)

    def upsert(self, key, doc):
        return self._collection.upsert(key, doc)

    def remove(self, key):
        return self._collection.remove(key)

    def query(self, strQuery, *options, **kwargs):
        # options are used for positional parameters
        # kwargs are used for named parameters

        # bucket.query() is different from cluster.query()
        return self._cluster.query(strQuery, *options, **kwargs)


# setup API endpoints

# setup app and APIs using Flask
app = Flask(__name__)


@app.route("/")
def start_page():
    """Function to load the splash screen mainly for gitpod demo as the initialization takes time4"""
    return render_template("splash_screen.html")


api = Api(
    app,
    version="1.0",
    title="Python API Quickstart - Profile",
    description="Couchbase Quickstart API with Python, Flask, and Flask-RestX",
    doc="/doc",
)
nsHealthCheck = api.namespace(
    "api/v1/healthcheck", description="Sanity check for unit tests"
)
nsProfile = api.namespace("api/v1/profile", "CRUD operations for Profile")

# setup models for post, put, search
profileInsert = api.model(
    "ProfileInsert",
    {
        "firstName": fields.String(required=False, description="User First Name"),
        "lastName": fields.String(required=False, description="User Last Name"),
        "email": fields.String(required=True, description="User Email Address"),
        "password": fields.String(
            required=True, description="User Password Unecrypted"
        ),
    },
)

profile = api.model(
    "Profile",
    {
        "pid": fields.String(required=True, description="ID of the document (UUID)"),
        "firstName": fields.String(required=False, description="User First Name"),
        "lastName": fields.String(required=False, description="User Last Name"),
        "email": fields.String(required=True, description="User Email Address"),
        "password": fields.String(
            required=True, description="User Password Unecrypted"
        ),
    },
)


@nsHealthCheck.route("/")
class HealthCheck(Resource):
    # tag::get[]
    def get(self):
        return jsonify(time=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

    # end::get[]


@nsProfile.route("")
class Profile(Resource):
    # tag::post[]
    @nsProfile.doc(
        "Create Profile",
        reponses={201: "Created", 409: "Key alreay exists", 500: "Unexpected Error"},
    )
    @nsProfile.expect(profileInsert, validate=True)
    @nsProfile.marshal_with(profile)
    def post(self):
        try:
            data = request.json
            # create new random key
            key = uuid.uuid4().__str__()
            data["pid"] = key
            # encrypt password
            hashed = bcrypt.hashpw(
                data["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode()
            data["password"] = hashed
            cb.insert(key, data)
            return data, 201
        except DocumentExistsException:
            return "Key already exists", 409
        except CouchbaseException as e:
            return f"Unexpected error: {e}", 500
        except Exception as e:
            return f"Unexpected error: {e}", 500

    # end::post[]


@nsProfile.route("/<id>")
class ProfileId(Resource):
    # tag::get[]
    @nsProfile.doc(
        "Get Profile",
        reponses={200: "Found document", 404: "Key not found", 500: "Unexpected Error"},
    )
    def get(self, id):
        try:
            res = cb.get(id)
            return jsonify(res.content_as[dict])
        except DocumentNotFoundException:
            return "Key not found", 404
        except CouchbaseException as e:
            return f"Unexpected error: {e}", 500

    # end::get[]

    # tag::put[]
    @nsProfile.doc(
        "Update Profile",
        reponses={
            200: "Document updated",
            404: "Document not found",
            500: "Unexpected Error",
        },
    )
    @nsProfile.expect(profileInsert)
    @nsProfile.marshal_with(profile)
    def put(self, id):
        try:
            data = request.json
            # create new random key
            data["pid"] = id
            # encrypt password
            hashed = bcrypt.hashpw(
                data["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode()
            data["password"] = hashed
            cb.upsert(id, data)
            return data
        except DocumentNotFoundException:
            # Document already deleted / never existed
            return "Key does not exist", 404
        except CouchbaseException as e:
            return f"Unexpected error: {e}", 500
        except Exception as e:
            return f"Unexpected error: {e}", 500

    # end::put[]

    # tag::delete[]
    @nsProfile.doc(
        "Delete Profile",
        reponses={
            200: "Delete document",
            404: "Document not found",
            500: "Unexpected Error",
        },
    )
    def delete(self, id):
        try:
            cb.remove(id)
            return "OK"
        except DocumentNotFoundException:
            # Document already deleted / never existed
            return "Key does not exist", 404
        except Exception as e:
            return f"Unexpected error: {e}", 500

    # end::delete[]


# tag::get[]
@nsProfile.route("/profiles")
class Profiles(Resource):
    @nsProfile.doc(
        "Find Profiles",
        reponses={201: "found", 500: "Unexpected Error"},
        params={
            "search": "value to search for",
            "limit": "int value of number of records to return",
            "skip": "int value of how many documents to skip",
        },
    )
    def get(self):
        try:
            # get vars from GET request
            search = request.args.get("search", "")
            limit = int(request.args.get("limit", 5))
            skip = int(request.args.get("skip", 0))

            search_str = f"%{search.lower()}%"

            # create query
            query = f"SELECT p.* FROM  {db_info['bucket']}.{db_info['scope']}.{db_info['collection']} p WHERE lower(p.firstName) LIKE $search_str OR lower(p.lastName) LIKE $search_str LIMIT $limit OFFSET $offset;"
            res = cb.query(query, limit=limit, offset=skip, search_str=search_str)

            # must loop through results
            # https://docs.couchbase.com/python-sdk/current/howtos/n1ql-queries-with-sdk.html#streaming-large-result-sets
            profiles = [x for x in res]

            return jsonify(profiles)
        # except
        except CouchbaseException as e:
            return f"Unexpected error: {e}", 500

    # end::get[]


load_dotenv()

db_info = {
    "host": os.getenv("DB_HOST"),
    "bucket": os.getenv("BUCKET"),
    "scope": os.getenv("SCOPE"),
    "collection": os.getenv("COLLECTION"),
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
}

cb = CouchbaseClient(*db_info.values())
cb.connect()

if __name__ == "__main__":
    app.run(debug=True)
