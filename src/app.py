from extensions import couchbase_db
from api.airport import airport_ns
from api.airline import airline_ns
from api.route import route_ns
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
    description="A quickstart API using Python with Couchbase, Flask & travel-sample data",
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
