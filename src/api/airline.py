from flask_restx import Namespace, fields, Resource
from flask import request
from extensions import couchbase_db
from couchbase.exceptions import (
    CouchbaseException,
    DocumentExistsException,
    DocumentNotFoundException,
)

AIRLINE_COLLECTION = "airline"

airline_ns = Namespace("Airline", description="Airline related APIs", ordered=True)

airline_model = airline_ns.model(
    "Airline",
    {
        "name": fields.String(
            required=True, description="Airline Name", example="Sample Airline"
        ),
        "iato": fields.String(description="IATA code"),
        "icao": fields.String(description="ICAO code"),
        "callsign": fields.String(required=True, description="Callsign"),
        "country": fields.String(required=True, description="Country"),
    },
)


@airline_ns.route("/<id>")
@airline_ns.doc(params={"id": "Airline ID like airline_10"})
class AirlineId(Resource):
    @airline_ns.doc(
        description="Create Airline",
        responses={
            201: "Created",
            409: "Airline already exists",
            500: "Unexpected Error",
        },
    )
    @airline_ns.expect(airline_model, validate=True)
    def post(self, id):
        try:
            data = request.json
            couchbase_db.insert_document(AIRLINE_COLLECTION, key=id, doc=data)
            return data, 201
        except DocumentExistsException as e:
            return "Airline already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airline_ns.doc(
        description="Get Airline",
        responses={
            200: "Found Airline",
            404: "Airline ID not found",
            500: "Unexpected Error",
        },
    )
    @airline_ns.marshal_with(airline_model, skip_none=True)
    def get(self, id):
        try:
            result = couchbase_db.get_document(AIRLINE_COLLECTION, key=id)
            return result.content_as[dict]
        except DocumentNotFoundException as e:
            return "Airline not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airline_ns.doc(
        description="Update Airline",
        responses={
            200: "Airline Updated",
            500: "Unexpected Error",
        },
    )
    @airline_ns.expect(airline_model, validate=True)
    def put(self, id):
        try:
            updated_doc = request.json
            couchbase_db.upsert_document(AIRLINE_COLLECTION, key=id, doc=updated_doc)
            return updated_doc
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airline_ns.doc(
        description="Delete Airline",
        responses={
            204: "Airline Deleted",
            404: "Airline not found",
            500: "Unexpected Error",
        },
    )
    def delete(self, id):
        try:
            couchbase_db.delete_document(AIRLINE_COLLECTION, key=id)
            return "Deleted", 204
        except DocumentNotFoundException:
            return "Airline not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@airline_ns.route("/list")
@airline_ns.doc(
    description="Get Airlines by Country",
    reponses={200: "List of airlines", 500: "Unexpected Error"},
    params={
        "country": {
            "description": "Country",
            "in": "query",
            "required": True,
            "example": "France",
        },
        "limit": {
            "description": "Number of airlines to return (page size)",
            "in": "query",
            "required": False,
            "default": 10,
        },
        "offset": {
            "description": "Number of airlines to skip (for pagination)",
            "in": "query",
            "required": False,
            "default": 0,
        },
    },
)
class AirlineList(Resource):
    @airline_ns.marshal_list_with(airline_model)
    def get(self):
        country = request.args.get("country", "")
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
        print(country, limit, offset)
        try:
            query = """
                SELECT airline.callsign,
                    airline.country,
                    airline.iata,
                    airline.icao,
                    airline.name
                FROM airline as airline 
                WHERE airline.country=$country 
                ORDER BY airline.name
                LIMIT $limit 
                OFFSET $offset;
            """
            result = couchbase_db.query(
                query, country=country, limit=limit, offset=offset
            )
            airlines = [r for r in result]
            return airlines
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@airline_ns.route("/to-airport")
@airline_ns.doc(
    description="Get Airlines flying to Airport",
    reponses={200: "List of airlines", 500: "Unexpected Error"},
    params={
        "airport": {
            "description": "Destination airport",
            "in": "query",
            "required": True,
            "example": "SFO",
        },
        "limit": {
            "description": "Number of airlines to return (page size)",
            "in": "query",
            "required": False,
            "default": 10,
        },
        "offset": {
            "description": "Number of airlines to skip (for pagination)",
            "in": "query",
            "required": False,
            "default": 0,
        },
    },
)
class AirlinesToAirport(Resource):
    @airline_ns.marshal_list_with(airline_model)
    def get(self):
        airport = request.args.get("airport", "")
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
        try:
            query = """
                SELECT air.callsign,
                    air.country,
                    air.iata,
                    air.icao,
                    air.name
                FROM (
                    SELECT DISTINCT META(airline).id AS airlineId
                    FROM route
                    JOIN airline ON route.airlineid = META(airline).id
                    WHERE route.destinationairport = $airport
                ) AS subquery
                JOIN airline AS air ON META(air).id = subquery.airlineId
                ORDER BY air.name
                LIMIT $limit OFFSET $offset;
            """
            result = couchbase_db.query(
                query, airport=airport, limit=limit, offset=offset
            )
            airports = [r for r in result]
            return airports
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500
