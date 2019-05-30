FROM bvlc/caffe:cpu

RUN apt-get update -qqy\
    && apt-get install -qy \
        unzip \
        python-tk \
        curl -qy \
    && pip install minio

RUN mkdir -p models resources \
    && curl -sL https://github.com/richzhang/colorization/raw/master/resources/pts_in_hull.npy > ./resources/pts_in_hull.npy \
    && curl -sL http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel > ./models/colorization_release_v2.caffemodel \
    && curl -sL https://raw.githubusercontent.com/richzhang/colorization/master/models/colorization_deploy_v2.prototxt > ./models/colorization_deploy_v2.prototxt

RUN curl -sSL https://github.com/openfaas/faas/releases/download/0.13.4/fwatchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ENV fprocess="python -u index.py"
ENV read_timeout="60"
ENV write_timeout="60"

RUN pip install requests

COPY index.py index.py
COPY handler.py handler.py

CMD ["fwatchdog"]
