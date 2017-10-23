FROM bvlc/caffe:cpu

RUN apt-get update && apt-get install unzip python-tk curl -qy
RUN pip install minio

RUN mkdir models resources
RUN wget https://github.com/richzhang/colorization/raw/master/resources/pts_in_hull.npy -O ./resources/pts_in_hull.npy
RUN wget http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel -O ./models/colorization_release_v2.caffemodel
RUN wget https://raw.githubusercontent.com/richzhang/colorization/master/models/colorization_deploy_v2.prototxt -O ./models/colorization_deploy_v2.prototxt

RUN curl -sSL https://github.com/openfaas/faas/releases/download/0.6.5/fwatchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ENV fprocess="python -u index.py"
ENV read_timeout="60"
ENV write_timeout="60"
ENV afterburn=true

COPY index.py index.py
COPY handler.py handler.py

CMD ["fwatchdog"]
