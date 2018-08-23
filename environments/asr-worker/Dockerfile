FROM docker-online-kaldi
MAINTAINER Aku Rouhe <aku.rouhe@aalto.fi>

WORKDIR /opt
RUN cd /opt && git clone https://github.com/Gastron/kaldi-gstreamer-server.git && \
    cd kaldi-gstreamer-server && \
    git checkout captaina && \
    rm -rf /opt/kaldi-gstreamer-server/.git/ && \
    rm -rf /opt/kaldi-gstreamer-server/test/

ADD requirements.txt /opt/requirements.txt
RUN apt-get update && apt-get install -y  \
    libffi-dev \
    python3-pip \
    python3-gi && \
    pip install --upgrade cffi && \
    pip3 install --upgrade cffi && \
    pip3 install tornado pyyaml ws4py==0.3.2


ENV GST_PLUGIN_PATH=/opt/gst-kaldi-nnet2-online/src/:/opt/kaldi/src/gst-plugin/

#Make this a volume with all the s5 style contents you need
WORKDIR /opt/s5

ENTRYPOINT ["python", "/opt/kaldi-gstreamer-server/kaldigstserver/worker.py"]
#Specify different command to run a different config:
CMD [ "-c", "/opt/asr-conf.yaml", "-u", "wss://tellme.aalto.fi/tellme-asr/worker/ws/speech" ]
