from extensions import couchbase_db
from api.airport import airport_ns
from api.airline import airline_ns
from api.route import route_ns
from api.hotel import hotel_ns
import os
from dotenv import load_dotenv
from flask import Flask
from flask_restx import Api

# Define the flask app and api
app = Flask(__name__)

# Disable field masks in the Swagger docs
# https://flask-restx.readthedocs.io/en/latest/mask.html
app.config["RESTX_MASK_SWAGGER"] = False

api = Api(
    title="Python Quickstart using Flask",
    version="1.0",
    description="""
    A quickstart API using Python with Couchbase, Flask & travel-sample data.

    We have a visual representation of the API documentation using Swagger which allows you to interact with the API's endpoints directly through the browser. It provides a clear view of the API including endpoints, HTTP methods, request parameters, and response objects. 
    
    Click on an individual endpoint to expand it and see detailed information. This includes the endpoint's description, possible response status codes, and the request parameters it accepts.

    Trying Out the API
    You can try out an API by clicking on the "Try it out" button next to the endpoints.
    
    - Parameters: If an endpoint requires parameters, Swagger UI provides input boxes for you to fill in. This could include path parameters, query strings, headers, or the body of a POST/PUT request.

    - Execution: Once you've inputted all the necessary parameters, you can click the "Execute" button to make a live API call. Swagger UI will send the request to the API and display the response directly in the documentation. This includes the response code, response headers, and response body.

    Models
    Swagger documents the structure of request and response bodies using models. These models define the expected data structure using JSON schema and are extremely helpful in understanding what data to send and expect.

    For details on the API, please check the tutorial on the Couchbase Developer Portal: https://developer.couchbase.com/tutorial-quickstart-flask-python/
    """,
)
api.init_app(app)

load_dotenv()

conn_str = os.getenv("DB_CONN_STR")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

if conn_str is None:
    print("DB_CONN_STR environment variable not set")
    exit()
if username is None:
    print("DB_USERNAME environment variable not set")
    exit()
if password is None:
    print("DB_PASSWORD environment variable not set")
    exit()

# Create the database connection
couchbase_db.init_app(conn_str, username, password, app)
couchbase_db.connect()

# Add the routes
api.add_namespace(airport_ns, path="/api/v1/airport")
api.add_namespace(airline_ns, path="/api/v1/airline")
api.add_namespace(route_ns, path="/api/v1/route")
api.add_namespace(hotel_ns, path="/api/v1/hotel")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
