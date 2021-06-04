FROM deniswsrosa/couchbase7.0.beta-gitpod

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive &&\ 
 apt-get install -y wget &&\
 apt-get install -y software-properties-common &&\
 apt-get update &&\ 
 apt-get install -y python3.8 &&\
 python -m pip install couchbase &&\
 python -m pip install flask &&\
 python -m pip install bcrypt &&\
 python -m pip install python-dotenv &&\
 export FLASK_APP=src/app &&\
 export FLASK_ENV=development