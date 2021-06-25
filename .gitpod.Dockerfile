FROM deniswsrosa/couchbase7-5868-gitpod

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive &&\ 
    apt-get install -y wget &&\
    apt-get install -y software-properties-common &&\
    apt-get install -y git-all python3-dev python3-pip python3-setuptools cmake build-essential &&\
    apt-get install -y python3.9 &&\
    apt-get install -y libssl-dev &&\
    apt-get update &&\ 
    export PATH="$PATH:/usr/local/bin" &&\
    export FLASK_APP=src/app &&\
    export FLASK_ENV=development
