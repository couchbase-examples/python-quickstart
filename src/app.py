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
api = Api(
    title="Python Quickstart using Flask",
    version="1.0",
    description="A quickstart API using Python with Couchbase, Flask & travel sample data",
)
api.init_app(app)


if __name__ == "__main__":
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
    api.add_namespace(airport_ns, path="/airport")
    api.add_namespace(airline_ns, path="/airline")
    api.add_namespace(route_ns, path="/route")

    app.run(debug=True, port=8080)
