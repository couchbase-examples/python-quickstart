from flask_restx import Namespace, fields, Resource
from flask import request
from extensions import couchbase_db
from couchbase.exceptions import (
    CouchbaseException,
    DocumentExistsException,
    DocumentNotFoundException,
)

ROUTE_COLLECTION = "route"
route_ns = Namespace("Route", description="Route related APIs", ordered=True)

schedule_fields = route_ns.model(
    "Schedule",
    {
        "day": fields.Integer(description="Day of week", example=0),
        "flight": fields.String(description="Flight Number", example="SF123"),
        "utc": fields.String(description="UTC Time", example="10:05:00"),
    },
)

route_model = route_ns.model(
    "Route",
    {
        "airline": fields.String(required=True, description="Airline", example="AF"),
        "airlineid": fields.String(
            required=True, description="Airline ID", example="airline_10"
        ),
        "sourceairport": fields.String(
            required=True, description="Source Airport", example="SFO"
        ),
        "destinationairport": fields.String(
            required=True, description="Destination Airport", example="JFK"
        ),
        "stops": fields.Integer(description="Stops", example=0),
        "equipment": fields.String(description="Equipment", example="CRJ"),
        "schedule": fields.List(fields.Nested(schedule_fields)),
        "distance": fields.Float(description="Distance in km", example=4151.79),
    },
)


@route_ns.route("/<id>")
@route_ns.doc(params={"id": "Route ID like route_10000"})
class RouteId(Resource):
    @route_ns.doc(
        description="Create Route with specified ID. \n\n This provides an example of using Key Value operations in Couchbase to create a new document with a specified ID.\n\n Code: `api/route.py` \n Class: `RouteId` \n Method: `post`",
        responses={
            201: "Created",
            409: "Route already exists",
            500: "Unexpected Error",
        },
    )
    @route_ns.expect(route_model, validate=True)
    def post(self, id):
        try:
            data = request.json
            couchbase_db.insert_document(ROUTE_COLLECTION, key=id, doc=data)
            return data, 201
        except DocumentExistsException:
            return "Route already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @route_ns.doc(
        description="Get Route with specified ID. \n\n This provides an example of using Key Value operations in Couchbase to get a document with specified ID.\n\n Code: `api/route.py` \n Class: `RouteId` \n Method: `get`",
        responses={
            200: "Route",
            404: "Route ID not found",
            500: "Unexpected Error",
        },
    )
    @route_ns.marshal_with(route_model, skip_none=True)
    def get(self, id):
        try:
            result = couchbase_db.get_document(ROUTE_COLLECTION, key=id)
            return result.content_as[dict]
        except DocumentNotFoundException:
            return "Route not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @route_ns.doc(
        description="Update Route with specified ID. \n\n This provides an example of using Key Value operations in Couchbase to upsert a document with specified ID.\n\n Code: `api/route.py` \n Class: `RouteId` \n Method: `put`",
        responses={
            200: "Route Updated",
            500: "Unexpected Error",
        },
    )
    @route_ns.expect(route_model, validate=True)
    def put(self, id):
        try:
            updated_doc = request.json
            couchbase_db.upsert_document(ROUTE_COLLECTION, key=id, doc=updated_doc)
            return updated_doc
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @route_ns.doc(
        description="Delete Route with specified ID. \n\n This provides an example of using Key Value operations in Couchbase to delete a document with specified ID.\n\n Code: `api/route.py` \n Class: `RouteId` \n Method: `delete`",
        responses={
            204: "Route Deleted",
            404: "Route not found",
            500: "Unexpected Error",
        },
    )
    def delete(self, id):
        try:
            couchbase_db.delete_document(ROUTE_COLLECTION, key=id)
            return "Deleted", 204
        except DocumentNotFoundException:
            return "Route not found", 404
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500
