from flask_restx import Namespace, fields, Resource
from flask import request
from extensions import couchbase_db
from couchbase.exceptions import (
    CouchbaseException,
    DocumentExistsException,
    DocumentNotFoundException,
)

AIRPORT_COLLECTION = "airport"

airport_ns = Namespace("Airport", description="Airport related APIs", ordered=True)

geo_cordinate_fields = airport_ns.model(
    "Geo Coordinates",
    {
        "lat": fields.Float(
            description="Latitude",
            example=48.864716,
        ),
        "lon": fields.Float(
            description="Longitude",
            example=2.349014,
        ),
        "alt": fields.Float(
            description="Altitude",
            example=92.0,
        ),
    },
)

airport_model = airport_ns.model(
    "Airport",
    {
        "airportname": fields.String(
            required=True, description="Airport Name", example="Sample Airport"
        ),
        "city": fields.String(required=True, description="City", example="Sample City"),
        "country": fields.String(
            required=True, description="Country", example="United Kingdom"
        ),
        "faa": fields.String(required=True, description="FAA code", example="SAA"),
        "icao": fields.String(description="ICAO code", example="SAAA"),
        "tz": fields.String(description="Timezone", example="Europe/Paris"),
        "geo": fields.Nested(geo_cordinate_fields),
    },
)


@airport_ns.route("/<id>")
@airport_ns.doc(params={"id": "Airport ID like airport_1273"})
class AirportId(Resource):
    @airport_ns.doc(
        description="Create Airport with specified ID. \n\n This provides an example of using [Key Value operations](https://docs.couchbase.com/python-sdk/current/howtos/kv-operations.html) in Couchbase to create a new document with a specified ID.\n\n Key Value operations are unique to Couchbase and provide very high speed get/set/delete operations.\n\n Code: [`api/airport.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/airport.py) \n Class: `AirportId` \n Method: `post`",
        responses={
            201: "Created",
            409: "Airport already exists",
            500: "Unexpected Error",
        },
    )
    @airport_ns.expect(airport_model, validate=True)
    def post(self, id):
        try:
            data = request.json
            couchbase_db.insert_document(AIRPORT_COLLECTION, key=id, doc=data)
            return data, 201
        except DocumentExistsException:
            return "Airport already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airport_ns.doc(
        description="Get Airport with specified ID. \n\n This provides an example of using [Key Value operations](https://docs.couchbase.com/python-sdk/current/howtos/kv-operations.html) in Couchbase to get a document with specified ID.\n\n Key Value operations are unique to Couchbase and provide very high speed get/set/delete operations.\n\n Code: [`api/airport.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/airport.py) \n Class: `AirportId` \n Method: `get`",
        responses={
            200: "Found Airport",
            404: "Airport ID not found",
            500: "Unexpected Error",
        },
    )
    @airport_ns.marshal_with(airport_model, skip_none=True)
    def get(self, id):
        try:
            result = couchbase_db.get_document(AIRPORT_COLLECTION, key=id)
            return result.content_as[dict]
        except DocumentNotFoundException:
            return "Airport not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airport_ns.doc(
        description="Update Airport with specified ID. \n\n This provides an example of using [Key Value operations](https://docs.couchbase.com/python-sdk/current/howtos/kv-operations.html) in Couchbase to upsert a document with specified ID.\n\n Key Value operations are unique to Couchbase and provide very high speed get/set/delete operations.\n\n Code: [`api/airport.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/airport.py) \n Class: `AirportId` \n Method: `put`",
        responses={
            200: "Airport Updated",
            500: "Unexpected Error",
        },
    )
    @airport_ns.expect(airport_model, validate=True)
    def put(self, id):
        try:
            updated_doc = request.json
            couchbase_db.upsert_document(AIRPORT_COLLECTION, key=id, doc=updated_doc)
            return updated_doc
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airport_ns.doc(
        description="Delete Airport with specified ID. \n\n This provides an example of using [Key Value operations](https://docs.couchbase.com/python-sdk/current/howtos/kv-operations.html) in Couchbase to delete a document with specified ID.\n\n Key Value operations are unique to Couchbase and provide very high speed get/set/delete operations.\n\n Code: [`api/airport.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/airport.py) \n Class: `AirportId` \n Method: `delete`",
        responses={
            204: "Airport Deleted",
            404: "Airport not found",
            500: "Unexpected Error",
        },
    )
    def delete(self, id):
        try:
            couchbase_db.delete_document(AIRPORT_COLLECTION, key=id)
            return "Deleted", 204
        except DocumentNotFoundException:
            return "Airport not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@airport_ns.route("/list")
@airport_ns.doc(
    description="Get list of Airports. Optionally, you can filter the list by Country. \n\n This provides an example of using a [SQL++ query](https://docs.couchbase.com/python-sdk/current/howtos/n1ql-queries-with-sdk.html) in Couchbase to fetch a list of documents matching the specified criteria.\n\n Code: [`api/airport.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/airport.py) \n Class: `AirportList` \n Method: `get`",
    reponses={200: "List of airports", 500: "Unexpected Error"},
    params={
        "country": {
            "description": "Country",
            "in": "query",
            "required": False,
            "example": "United Kingdom, France, United States",
        },
        "limit": {
            "description": "Number of airports to return (page size)",
            "in": "query",
            "required": False,
            "default": 10,
        },
        "offset": {
            "description": "Number of airports to skip (for pagination)",
            "in": "query",
            "required": False,
            "default": 0,
        },
    },
)
class AirportList(Resource):
    @airport_ns.marshal_list_with(airport_model)
    def get(self):
        country = request.args.get("country", "")
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        if country:
            query = """
                SELECT airport.airportname,
                    airport.city,
                    airport.country,
                    airport.faa,
                    airport.geo,
                    airport.icao,
                    airport.tz
                FROM airport AS airport
                WHERE airport.country = $country
                ORDER BY airport.airportname
                LIMIT $limit
                OFFSET $offset;
            """
        else:
            query = """
                SELECT airport.airportname,
                    airport.city,
                    airport.country,
                    airport.faa,
                    airport.geo,
                    airport.icao,
                    airport.tz
                FROM airport AS airport
                ORDER BY airport.airportname
                LIMIT $limit
                OFFSET $offset;
            """
        try:
            results = couchbase_db.query(
                query, country=country, limit=limit, offset=offset
            )
            airports = [r for r in results]
            return airports
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


destination_airports_model = airport_ns.model(
    "Direct Connections",
    {
        "destinationairport": fields.String(
            required=True, description="Airport FAA Code", example="JFK"
        ),
    },
)


@airport_ns.route("/direct-connections")
@airport_ns.doc(
    description="Get Direct Connections from specified Airport. \n\n This provides an example of using a [SQL++ query](https://docs.couchbase.com/python-sdk/current/howtos/n1ql-queries-with-sdk.html) in Couchbase to fetch a list of documents matching the specified criteria.\n\n Code: [`api/airport.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/airport.py) \n Class: `DirectConnections` \n Method: `get`",
    reponses={200: "List of direct connections", 500: "Unexpected Error"},
    params={
        "airport": {
            "description": "Source airport",
            "in": "query",
            "required": True,
            "example": "SFO, LHR, CDG",
        },
        "limit": {
            "description": "Number of direct connections to return (page size)",
            "in": "query",
            "required": False,
            "default": 10,
        },
        "offset": {
            "description": "Number of direct connections to skip (for pagination)",
            "in": "query",
            "required": False,
            "default": 0,
        },
    },
)
class DirectConnections(Resource):
    @airport_ns.marshal_list_with(destination_airports_model)
    def get(self):
        airport = request.args.get("airport", "")
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        try:
            query = """
                SELECT distinct (route.destinationairport)
                FROM airport as airport
                JOIN route as route on route.sourceairport = airport.faa
                WHERE airport.faa = $airport and route.stops = 0
                ORDER BY route.destinationairport
                LIMIT $limit
                OFFSET $offset
            """
            result = couchbase_db.query(
                query, airport=airport, limit=limit, offset=offset
            )
            airports = [r for r in result]
            return airports
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500
