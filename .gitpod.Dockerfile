FROM couchbase:latest

RUN echo "* soft nproc 20000\n"\
    "* hard nproc 20000\n"\
    "* soft nofile 200000\n"\
    "* hard nofile 200000\n" >> /etc/security/limits.conf

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive &&\ 
    apt-get install -y wget &&\
    apt-get install -y software-properties-common &&\
    apt-get install -y git-all python3-dev python3-pip python3-setuptools cmake build-essential libffi-dev &&\
    apt-get install -y python3.9 &&\
    apt-get install -y libssl-dev &&\
    apt-get install -y socat sudo &&\
    apt-get update &&\ 
    export PATH="$PATH:/usr/local/bin" &&\
    export FLASK_APP=src/app &&\
    export FLASK_ENV=development

RUN addgroup --gid 33333 gitpod && \
    useradd --no-log-init --create-home --home-dir /home/gitpod --shell /bin/bash --uid 33333 --gid 33333 gitpod && \
    usermod -a -G gitpod,couchbase,sudo gitpod && \
    echo 'gitpod ALL=(ALL) NOPASSWD:ALL'>> /etc/sudoers

COPY startcb.sh /opt/couchbase/bin/startcb.sh
# COPY src/requirements.txt requirements.txt
USER gitpod
