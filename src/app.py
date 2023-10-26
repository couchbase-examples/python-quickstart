from db import CouchbaseClient
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_restx import Api, Namespace, fields, Resource
from couchbase.exceptions import (
    CouchbaseException,
    DocumentNotFoundException,
    DocumentExistsException,
)

app = Flask(__name__)
api = Api(
    title="Python Quickstart using Flask",
    version="1.0",
    description="A quickstart API using Python with Couchbase, Flask & travel data",
)
api.init_app(app)
airport_ns = Namespace("Airports", description="Airport related APIs", ordered=True)

airport_model = airport_ns.model(
    "Airport",
    {
        "id": fields.String(
            required=True, description="airport id", example="airport_1273"
        ),
        "airportname": fields.String(required=True, description="airport name"),
        "city": fields.String(required=True, description="city"),
        "country": fields.String(required=True, description="country"),
        "faa": fields.String(required=True, description="faa"),
        "icao": fields.String(description="icao"),
        "tz": fields.String(description="timezone"),
        "geo.lat": fields.Float(description="latitude"),
        "geo.lon": fields.Float(description="longitude"),
        "geo.alt": fields.Float(description="altitude"),
    },
)


@airport_ns.route("")
class Airport(Resource):
    @airport_ns.doc(
        "Create Airport",
        responses={
            201: "Created",
            409: "Airport already exists",
            500: "Unexpected Error",
        },
    )
    @airport_ns.expect(airport_model, validate=True)
    def post(self):
        try:
            data = request.json
            couchbase_dao.insert_document("airport", data["id"], data)
            return data, 201
        except DocumentExistsException as e:
            return "Airport already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@airport_ns.route("/<id>")
@airport_ns.doc(params={"id": "airport id"})
class AirportId(Resource):
    @airport_ns.doc(
        "Get Airport",
        responses={
            200: "Found Airport",
            404: "Airport ID not found",
            500: "Unexpected Error",
        },
    )
    def get(self, id):
        try:
            result = couchbase_dao.get_document("airport", id)
            return jsonify(result.content_as[dict])
        except DocumentNotFoundException as e:
            return "Airport not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airport_ns.doc(
        "Update Airport",
        responses={
            200: "Airport Updated",
            500: "Unexpected Error",
        },
    )
    @airport_ns.expect(airport_model)
    def put(self, id):
        try:
            updated_doc = request.json
            couchbase_dao.upsert_document("airport", id, updated_doc)
            return updated_doc
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airport_ns.doc(
        "Delete Airport",
        responses={
            204: "Airport Deleted",
            404: "Airport not found",
            500: "Unexpected Error",
        },
    )
    def delete(self, id):
        try:
            couchbase_dao.delete_document("airport", id)
            return "Deleted", 204
        except DocumentNotFoundException:
            return "Airport not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


if __name__ == "__main__":
    load_dotenv()

    conn_str = os.getenv("DB_HOST")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if conn_str is None:
        print("DB_HOST environment variable not set")
        exit()
    if username is None:
        print("USERNAME environment variable not set")
        exit()
    if password is None:
        print("PASSWORD environment variable not set")
        exit()

    couchbase_dao = CouchbaseClient(conn_str, username, password, True)
    couchbase_dao.connect()

    api.add_namespace(airport_ns, path="/airport")

    app.run(debug=True, port=8080)
