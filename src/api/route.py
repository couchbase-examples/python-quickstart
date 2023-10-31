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
        "airline_id": fields.String(
            required=True, description="Airline ID", example="airline_10"
        ),
        "sourceairport": fields.String(
            required=True, description="Source Airport", example="SFO"
        ),
        "destinationairport": fields.String(
            required=True, description="Destination Airport", example="JFK"
        ),
        "stops": fields.Integer(description="Stops"),
        "equipment": fields.String(description="Equipment", example="CRJ"),
        "schedule": fields.List(fields.Nested(schedule_fields)),
        "distance": fields.Float(description="Distance in km", example=4151.79),
    },
)


@route_ns.route("/<id>")
@route_ns.doc(params={"id": "Route ID like route_10000"})
class RouteId(Resource):
    @route_ns.doc(
        description="Create Route",
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
        except DocumentExistsException as e:
            return "Route already exists", 409
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500

    @route_ns.doc(
        description="Get Route",
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
        description="Update Route",
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
        description="Delete Route",
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
