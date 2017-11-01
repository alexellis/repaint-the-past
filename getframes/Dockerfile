FROM python:2.7
RUN apt-get update -qy \
  && apt-get install -qy \
     nano wget build-essential libmp3lame-dev \
     libvorbis-dev libtheora-dev libspeex-dev \
     yasm pkg-config libopenjpeg-dev libx264-dev libav-tools
RUN pip install numpy \
    && pip install opencv-python scikit-video

WORKDIR /root
RUN wget http://ffmpeg.org/releases/ffmpeg-3.4.tar.bz2 \
    && tar xvjf ffmpeg-3.4.tar.bz2

WORKDIR /root/ffmpeg-3.4

RUN ./configure --enable-gpl --enable-postproc --enable-swscale --enable-avfilter --enable-libmp3lame \
  --enable-libvorbis --enable-libtheora --enable-libx264 --enable-libspeex --enable-shared --enable-pthreads \
  --enable-libopenjpeg --enable-nonfree \
    && make -j 4 \
    && make install \
    && /sbin/ldconfig

WORKDIR /tmp/

CMD ["/bin/bash"]
