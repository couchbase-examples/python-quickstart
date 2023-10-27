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

AIRPORT_COLLECTION = "airport"
AIRLINE_COLLECTION = "airline"
ROUTE_COLLECTION = "route"

app = Flask(__name__)
api = Api(
    title="Python Quickstart using Flask",
    version="1.0",
    description="A quickstart API using Python with Couchbase, Flask & travel data",
)
api.init_app(app)
airport_ns = Namespace("Airport", description="Airport related APIs", ordered=True)

airport_model = airport_ns.model(
    "Airport",
    {
        "id": fields.String(
            required=True, description="airport ID", example="airport_1273"
        ),
        "type": fields.String(description="document type", default="airport"),
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
            couchbase_dao.insert_document(AIRPORT_COLLECTION, data["id"], data)
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
            result = couchbase_dao.get_document(AIRPORT_COLLECTION, id)
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
            couchbase_dao.upsert_document(AIRPORT_COLLECTION, id, updated_doc)
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
            couchbase_dao.delete_document(AIRPORT_COLLECTION, id)
            return "Deleted", 204
        except DocumentNotFoundException:
            return "Airport not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


airline_ns = Namespace("Airline", description="Airline related APIs", ordered=True)

airline_model = airline_ns.model(
    "Airline",
    {
        "id": fields.String(
            required=True, description="Airline ID", example="airline_10"
        ),
        "name": fields.String(required=True, description="airline name"),
        "type": fields.String(description="document type", default="airline"),
        "iato": fields.String(description="iata"),
        "icao": fields.String(description="icao"),
        "callsign": fields.String(required=True, description="callsign"),
        "country": fields.String(required=True, description="country"),
    },
)


@airline_ns.route("")
class Airline(Resource):
    @airline_ns.doc(
        "Create Airline",
        responses={
            201: "Created",
            409: "Airline already exists",
            500: "Unexpected Error",
        },
    )
    @airline_ns.expect(airline_model, validate=True)
    def post(self):
        try:
            data = request.json
            couchbase_dao.insert_document(AIRLINE_COLLECTION, data["id"], data)
            return data, 201
        except DocumentExistsException as e:
            return "Airline already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@airline_ns.route("/<id>")
@airline_ns.doc(params={"id": "airline id"})
class AirlineId(Resource):
    @airline_ns.doc(
        "Get Airline",
        responses={
            200: "Found Airline",
            404: "Airline ID not found",
            500: "Unexpected Error",
        },
    )
    def get(self, id):
        try:
            result = couchbase_dao.get_document(AIRLINE_COLLECTION, id)
            return jsonify(result.content_as[dict])
        except DocumentNotFoundException as e:
            return "Airline not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airline_ns.doc(
        "Update Airline",
        responses={
            200: "Airline Updated",
            500: "Unexpected Error",
        },
    )
    @airline_ns.expect(airline_model, validate=True)
    def put(self, id):
        try:
            updated_doc = request.json
            couchbase_dao.upsert_document(AIRLINE_COLLECTION, id, updated_doc)
            return updated_doc
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airline_ns.doc(
        "Delete Airline",
        responses={
            204: "Airline Deleted",
            404: "Airline not found",
            500: "Unexpected Error",
        },
    )
    def delete(self, id):
        try:
            couchbase_dao.delete_document(AIRLINE_COLLECTION, id)
            return "Deleted", 204
        except DocumentNotFoundException:
            return "Airline not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


route_ns = Namespace("Route", description="Route related APIs", ordered=True)

route_model = route_ns.model(
    "Route",
    {
        "id": fields.String(required=True, description="Route ID", example="route_10"),
        "type": fields.String(description="document type", default="route"),
        "airline": fields.String(required=True, description="airline"),
        "airline_id": fields.String(required=True, description="airline id"),
        "sourceairport": fields.String(required=True, description="source airport"),
        "destinationairport": fields.String(
            required=True, description="destination airport"
        ),
        "stops": fields.Integer(description="stops"),
        "equipment": fields.String(description="equipment"),
        # "schedule": fields.Wildcard(description="schedule"),
        "distance": fields.Float(description="distance"),
    },
)


@route_ns.route("/")
class Route(Resource):
    @route_ns.doc(
        "Create Route",
        responses={
            201: "Created",
            409: "Route already exists",
            500: "Unexpected Error",
        },
    )
    @route_ns.expect(route_model, validate=True)
    def post(self):
        try:
            data = request.json
            couchbase_dao.insert_document(ROUTE_COLLECTION, data["id"], data)
            return data, 201
        except DocumentExistsException as e:
            return "Route already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@route_ns.route("/<id>")
@route_ns.doc(params={"id": "route id"})
class RouteId(Resource):
    @route_ns.doc(
        "Get Route",
        responses={
            200: "Route",
            404: "Route ID not found",
            500: "Unexpected Error",
        },
    )
    def get(self, id):
        try:
            result = couchbase_dao.get_document(ROUTE_COLLECTION, id)
            return jsonify(result.content_as[dict])
        except DocumentNotFoundException:
            return "Route not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @route_ns.doc(
        "Update Route",
        responses={
            200: "Route Updated",
            500: "Unexpected Error",
        },
    )
    @route_ns.expect(route_model, validate=True)
    def put(self, id):
        try:
            updated_doc = request.json
            couchbase_dao.upsert_document(ROUTE_COLLECTION, id, updated_doc)
            return updated_doc
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @route_ns.doc(
        "Delete Route",
        responses={
            204: "Route Deleted",
            404: "Route not found",
            500: "Unexpected Error",
        },
    )
    def delete(self, id):
        try:
            couchbase_dao.delete_document(ROUTE_COLLECTION, id)
            return "Deleted", 204
        except DocumentNotFoundException:
            return "Route not found", 404
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
    api.add_namespace(airline_ns, path="/airline")
    api.add_namespace(route_ns, path="/route")

    app.run(debug=True, port=8080)
