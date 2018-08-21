FROM tiangolo/uwsgi-nginx-flask:python3.5
MAINTAINER Aku Rouhe <aku.rouhe@aalto.fi>

WORKDIR /app
ADD uwsgi.ini /app/uwsgi.ini 
ADD requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
