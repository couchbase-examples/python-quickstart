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
        "iato": fields.String(description="IATA code", example="SA"),
        "icao": fields.String(description="ICAO code", example="SAF"),
        "callsign": fields.String(required=True, description="Callsign", example="SAF"),
        "country": fields.String(
            required=True, description="Country", example="United States"
        ),
    },
)


@airline_ns.route("/<id>")
@airline_ns.doc(params={"id": "Airline ID like airline_10"})
class AirlineId(Resource):
    @airline_ns.doc(
        description="Create Airline with specified ID.\n\n This provides an example of using Key Value operations in Couchbase to create a new document with a specified ID.\n\n Code: `api/airline.py` \n Class: `AirlineId` \n Method: `post`",
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
        description="Get Airline with specified ID. \n\n This provides an example of using Key Value operations in Couchbase to get a document with specified ID.\n\n Code: `api/airline.py` \n Class: `AirlineId` \n Method: `get`",
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
        description="Update Airline with specified ID. \n\n This provides an example of using Key Value operations in Couchbase to upsert a document with specified ID.\n\n Code: `api/airline.py` \n Class: `AirlineId` \n Method: `put`",
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
        description="Delete Airline with specified ID. \n\n This provides an example of using Key Value operations in Couchbase to delete a document with specified ID.\n\n Code: `api/airline.py` \n Class: `AirlineId` \n Method: `delete`",
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
    description="Get list of Airlines. Optionally, you can filter the list by Country. \n\n This provides an example of using SQL++ query in Couchbase to fetch a list of documents matching the specified criteria.\n\n Code: `api/airline.py` \n Class: `AirlineList` \n Method: `get`",
    reponses={200: "List of airlines", 500: "Unexpected Error"},
    params={
        "country": {
            "description": "Country",
            "in": "query",
            "required": False,
            "example": "France, United Kingdom, United States",
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
        if country:
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

        else:
            query = """
                SELECT airline.callsign,
                    airline.country,
                    airline.iata,
                    airline.icao,
                    airline.name
                FROM airline as airline 
                ORDER BY airline.name
                LIMIT $limit 
                OFFSET $offset;
            """

        try:
            result = couchbase_db.query(
                query, country=country, limit=limit, offset=offset
            )
            airlines = [r for r in result]
            return airlines
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@airline_ns.route("/to-airport")
@airline_ns.doc(
    description="Get Airlines flying to specified destination Airport. \n\n This provides an example of using SQL++ query in Couchbase to fetch a list of documents matching the specified criteria.\n\n Code: `api/airline.py` \n Class: `AirlinesToAirport` \n Method: `get`",
    reponses={200: "List of airlines", 500: "Unexpected Error"},
    params={
        "airport": {
            "description": "Destination airport",
            "in": "query",
            "required": True,
            "example": "SFO, JFK, LAX",
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
                LIMIT $limit 
                OFFSET $offset;
            """
            result = couchbase_db.query(
                query, airport=airport, limit=limit, offset=offset
            )
            airports = [r for r in result]
            return airports
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500
