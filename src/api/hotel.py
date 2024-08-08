from flask_restx import Namespace, fields, Resource
from flask import request
from extensions import couchbase_db
from couchbase.exceptions import CouchbaseException

hotel_COLLECTION = "hotel"
hotel_ns = Namespace("Hotel", description="Hotel related APIs", ordered=True)

hotel_name_model = hotel_ns.model(
    "HotelName", {"name": fields.String(required=True, description="Hotel Name")}
)

hotel_model = hotel_ns.model(
    "Hotel",
    {
        "city": fields.String(description="Hotel Name", example="Santa Margarita"),
        "country": fields.String(description="Country Name", example="United States"),
        "description": fields.String(
            description="Description", example="newly renovated"
        ),
        "name": fields.String(description="Name", example="KCL Campground"),
        "state": fields.String(description="state", example="California"),
        "title": fields.String(
            description="title", example="Carrizo Plain National Monument"
        ),
    },
)


@hotel_ns.route("/autocomplete")
class HotelAutoComplete(Resource):
    @hotel_ns.doc(
        description="Search for hotels based on their name. \n\n This provides an example of using [Search operations](https://docs.couchbase.com/python-sdk/current/howtos/full-text-searching-with-sdk.html#search-queries) in Couchbase to search for a specific name using the fts index.\n\n Code: [`api/hotel.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/hotel.py) \n Class: `HotelAutoComplete` \n Method: `get`",
        responses={
            200: "List of Hotel Names",
            500: "Unexpected Error",
        },
    )
    @hotel_ns.marshal_with(hotel_name_model)
    @hotel_ns.doc(params={"name": "Hotel Name like Seal View"})
    def get(self):
        name = request.args.get("name", "")
        try:
            result = couchbase_db.search_by_name(name=name)
            return [{"name": name} for name in result], 200
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500


@hotel_ns.route("/filter")
class HotelFilter(Resource):
    @hotel_ns.marshal_list_with(hotel_model)
    @hotel_ns.doc(
        description="Filter hotels using various filters such as name, title, description, country, state and city. \n\n This provides an example of using [Search operations](https://docs.couchbase.com/python-sdk/current/howtos/full-text-searching-with-sdk.html#search-queries) in Couchbase to filter documents using the fts index.\n\n Code: [`api/hotel.py`](https://github.com/couchbase-examples/python-quickstart/blob/main/src/api/hotel.py) \n Class: `HotelFilter` \n Method: `post`",
        responses={
            200: "List of Hotels",
            500: "Unexpected Error",
        },
        params={
            "limit": {
                "description": "Number of hotels to return (page size)",
                "in": "query",
                "required": False,
                "default": 10,
            },
            "offset": {
                "description": "Number of hotels to skip (for pagination)",
                "in": "query",
                "required": False,
                "default": 0,
            },
        },
    )
    @hotel_ns.expect(hotel_model, validate=True)
    def post(self):
        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
            data = request.json
            hotels = couchbase_db.filter(data, limit=limit, offset=offset)
            return hotels, 200
        except (CouchbaseException, Exception) as e:
            return f"Unexpected error: {e}", 500
