# Quickstart in Couchbase with Flask and Python

#### Build a REST API with Couchbase's Python SDK 3 and Flask

> This repo is designed to teach you how to connect to a Couchbase cluster to create, read, update, and delete documents and how to write simple parametrized N1QL queries.

[![Try it now!](https://da-demo-images.s3.amazonaws.com/runItNow_outline.png?couchbase-example=python-flaskquickstart-repo&source=github)](https://gitpod.io/#https://github.com/couchbase-examples/python-quickstart)

Full documentation can be found on the [Couchbase Developer Portal](https://developer.couchbase.com/tutorial-quickstart-flask-python/).

## Prerequisites

To run this prebuilt project, you will need:

- Couchbase 7 Installed
- [Python v3.x](https://www.python.org/downloads/) installed
- Code Editor installed

### Install Dependencies

Dependencies can be installed through PIP the default package manage for Python.

```sh
python -m pip install -r requirements.txt
```

### Database Server Configuration

All configuration for communication with the database is stored in the `.env` file in the src folder. This includes the connection string, username, password, bucket name, colleciton name, and scope name.

There is an example file `.env.example` that can be used as the template for the pararmeters for your environment. You can copy this file and fill in with the values corresponding to your environment.

## Running The Application

At this point the application is ready and you can run it:

```sh
cd src
flask run
```

> \*Couchbase 7 must be installed and running on localhost (http://127.0.0.1:8091) prior to running the Flask Python app.

## Running The Tests

To run the standard integration tests, use the following commands:

```sh
cd src
pytest test.py
```

## Conclusion

Setting up a basic REST API in Flask and Python with Couchbase is fairly simple. In this project when ran with Couchbase Server 7 installed, it will create a bucket in Couchbase, an index for our parameterized [N1QL query](https://docs.couchbase.com/python-sdk/current/howtos/n1ql-queries-with-sdk.html), and showcases basic CRUD operations needed in most applications.
