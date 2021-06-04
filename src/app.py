'''
python -m pip install couchbase
python -m pip install flask
python -m pip install bcrypt
python -m pip install python-dotenv

export FLASK_APP=src/app && \
export FLASK_ENV=development

NOTE:  make sure to change into the src 
    directory before running flask

flask run
'''
#setup flask
from flask import Flask, jsonify, request
from codecs import decode

#setup couchbase
from couchbase.management.buckets import BucketSettings 
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import *
from couchbase.management.collections import CollectionSpec
from couchbase.diagnostics import PingState

from datetime import datetime

import uuid 
import time
import bcrypt

class CouchbaseClient(object):

    @classmethod
    def create_client(_, *args, **kwargs):
        self = CouchbaseClient(*args)
        connected = self.ping()
        if not connected:
            self.connect(**kwargs)
        return self

    _instance = None

    def __new__(cls, host, bucket, collection, scope, username, pw):
        if CouchbaseClient._instance is None:
            CouchbaseClient._instance = object.__new__(cls)
            CouchbaseClient._instance.host = host
            CouchbaseClient._instance.bucket_name = bucket
            CouchbaseClient._instance.collection_name = collection
            CouchbaseClient._instance.scope_name = scope 
            CouchbaseClient._instance.username = username
            CouchbaseClient._instance.password = pw
        return CouchbaseClient._instance

    def connect(self, **kwargs):
        # note: kwargs would be how one could pass in
        #       more info for client config
        conn_str = 'couchbase://{0}'.format(self.host)

        try:
            cluster_opts = ClusterOptions(
                authenticator=PasswordAuthenticator(
                    self.username, self.password))
            self._cluster = Cluster(conn_str, options=cluster_opts)

        except CouchbaseException as error:
            print('Could not connect to cluster. Error: {}'.format(error))
            raise

        try:
            #create bucket if it doesn't exist
            bucketSettings = BucketSettings(name = self.bucket_name, ram_quota_mb=256)
            self._cluster.buckets().create_bucket(bucketSettings)
        except BucketAlreadyExistsException:
            print('bucket already exists')

        self._bucket = self._cluster.bucket(self.bucket_name)

        try:
            #create collection if it doesn't exist
            colSpec = CollectionSpec(self.collection_name, self.scope_name) 
            self._bucket.collections().create_collection(colSpec)
            
        except CollectionAlreadyExistsException:
            print ('collection already exists')

        self._collection = self._bucket.collection(self.collection_name)


        #create index if it doesn't exist
        time.sleep(5)
        try:
            #create index if it doesn't exist
            createIndexProfile = "CREATE PRIMARY INDEX default_profile_index ON " + self.bucket_name + "." + self.scope_name + "." + self.collection_name 
            createIndex = "CREATE PRIMARY INDEX ON " + self.bucket_name 

            self._bucket.query(createIndexProfile).execute()
            self._bucket.query(createIndex).execute()
        except QueryIndexAlreadyExistsException:
            print ('index already exists')
        except Exception as e:
            print (f"Error: {e}")

    def ping(self):
        try:
            # if couchbase version >= 3.0.10:
            # else use self._bucket.ping()
            result = self._cluster.ping()
            for _, reports in result.endpoints.items():
                for report in reports:
                    if not report.state == PingState.OK:
                        return False
            return True
        except AttributeError:
            # if the _cluster attr doesn't exist, neither does the client
            return False

    def get(self, key):
        return self._collection.get(key)

    def insert(self, key, doc):
        return self._collection.insert(key, doc)

    def upsert(self, key, doc):
        return self._collection.upsert(key, doc)

    def remove(self, key):
        return self._collection.remove(key)

    def query(self, strQuery):
        return self._bucket.query(strQuery)

#setup app and api's using Flask
app = Flask(__name__)

#setup API endpoints

# tag::get[]
@app.route('/api/v1/healthCheck/', methods=['GET'])
def healthCheck():
    return "{\"time\": \"" + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "\"}"
#end::get[]

# tag::post[]
@app.route('/api/v1/profile/', methods=['POST'])
def post():
    try:
        data = request.json
        #create new random key
        key = uuid.uuid4().__str__()
        data["pid"] = key
        #encrypt password
        hashed = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt()).decode()
        data["password"] = hashed
        cb.insert(key, data)
        return data, 201
    except DocumentExistsException:
        return 'Key already exists', 409
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500
    except Exception as e:
        return 'Unexpected error: {}'.format(e), 500
# end::post[]

# tag::get[]
@app.route('/api/v1/profile/<key>', methods=['GET'])
def get(key):
    try:
        res = cb.get(key)
        return jsonify(res.content_as[dict])  
    except DocumentNotFoundException:
        return 'Key not found', 404
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500
# end::get[]    

# tag::put[]
@app.route('/api/v1/profile/<key>', methods=['PUT'])
def put(key):
    try:
        cb.upsert(key, request.json)
        return 'OK'
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500
# end::put[]

# tag::delete[]
@app.route('/api/v1/profile/<key>', methods=['DELETE'])
def delete(key):
    try:
        cb.remove(key)
        return 'OK'
    except DocumentNotFoundException:
        # Document already deleted / never existed
        return 'Key does not exist', 404
# end::delete[]


# tag::get[]
@app.route('/api/v1/profiles', methods=['GET'])
def getProfiles():
    try:
        #get vars from GET request
        search = request.args.get("search")
        limit = request.args.get("limit")
        skip = request.args.get("skip")

        #create query
        query = f"SELECT p.* FROM  {db_info['bucket']}.{db_info['scope']}.{db_info['collection']} p WHERE lower(p.firstName) LIKE '%{search.lower()}%' OR lower(p.lastName) LIKE '%{search.lower()}%' LIMIT {limit} OFFSET {skip}"
        res = cb.query(query)

        #must loop through results
        #https://docs.couchbase.com/python-sdk/current/howtos/n1ql-queries-with-sdk.html#streaming-large-result-sets
        profiles = []
        for x in res:
            profiles.append(x)
        return jsonify(profiles)  
    except DocumentNotFoundException:
        return 'Key not found', 404
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500
# end::get[]   

# done for example purposes only, some
# sort of configuration should be used
db_info = {
    'host': 'localhost',
    'bucket': 'user_profile',
    'collection': 'profile',
    'scope': '_default',
    'username': 'Administrator',
    'password': 'password'
}

cb = CouchbaseClient.create_client(*db_info.values())

if __name__ == "__main__":
    app.run(debug=True)