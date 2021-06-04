FROM deniswsrosa/couchbase7.0.beta-gitpod

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive &&\ 
 apt-get install -y wget &&\
 apt-get install -y software-properties-common &&\
 apt-get install -y python3.9 &&\
 apt-get install -y python3-pip &&\
 apt-get install -y docutils  &&\
 apt-get update &&\ 
 export PATH="$PATH:/usr/local/bin" &&\
 python3 -m pip install couchbase &&\
 python3 -m pip install flask &&\
 python3 -m pip install bcrypt &&\
 python3 -m pip install python-dotenv &&\
 export FLASK_APP=src/app &&\
 export FLASK_ENV=development