FROM docker-online-kaldi
MAINTAINER Aku Rouhe <aku.rouhe@aalto.fi>

WORKDIR /opt

#Requirements for using captaina/models
ADD requirements.txt /opt/requirements.txt
RUN apt-get update && apt-get install -y  \
    libffi-dev \
    python3-pip \
    python3-gi && \
    pip3 install --upgrade cffi && \
    pip3 install -r /opt/requirements.txt && \
    pip3 install tornado pyyaml ws4py==0.3.2

ENTRYPOINT ["python3", "/opt/kaldi-gstreamer-server/kaldigstserver/master_server.py"]
