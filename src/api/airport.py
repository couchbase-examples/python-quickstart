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
        "country": fields.String(required=True, description="Country"),
        "faa": fields.String(required=True, description="FAA code"),
        "icao": fields.String(description="ICAO code"),
        "tz": fields.String(description="Timezone", example="Europe/Paris"),
        "geo": fields.Nested(geo_cordinate_fields),
    },
)


@airport_ns.route("/<id>")
@airport_ns.doc(params={"id": "Airport ID like airport_1273"})
class AirportId(Resource):
    @airport_ns.doc(
        description="Create Airport",
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
        except DocumentExistsException as e:
            return "Airport already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airport_ns.doc(
        description="Get Airport",
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
        except DocumentNotFoundException as e:
            return "Airport not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @airport_ns.doc(
        description="Update Airport",
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
        description="Delete Airport",
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
    description="Get Airports by Country",
    reponses={200: "List of airports", 500: "Unexpected Error"},
    params={
        "country": {"description": "Country", "in": "query", "required": True},
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

        try:
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
    description="Get Direct Connections from Airport",
    reponses={200: "List of direct connections", 500: "Unexpected Error"},
    params={
        "airport": {
            "description": "Airport",
            "in": "query",
            "required": True,
            "example": "SFO",
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
