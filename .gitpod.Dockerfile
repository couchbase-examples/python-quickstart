FROM deniswsrosa/couchbase7.0.beta-gitpod

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive &&\ 
 apt-get install -y wget &&\
 apt-get install -y software-properties-common &&\
 apt-get update &&\ 
 apt-get install -y python3.8 &&\
 export PATH="$PATH:/usr/local/bin" &&\
 python3 -m pip3 install couchbase &&\
 python3 -m pip3 install flask &&\
 python3 -m pip3 install bcrypt &&\
 python3 -m pip3 install python-dotenv &&\
 export FLASK_APP=src/app &&\
 export FLASK_ENV=development