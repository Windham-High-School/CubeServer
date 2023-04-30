FROM aler9/rtsp-simple-server:latest
FROM linuxserver/ffmpeg:latest

RUN apt-get update && apt-get install -y gettext moreutils

COPY --from=0 /mediamtx /mediamtx

COPY Docker/ipcam/start.sh /start.sh
COPY Docker/ipcam/mediamtx.yml /mediamtx.yml
COPY Docker/ipcam/ffmpeg_stream.sh /ffmpeg_stream.sh

ARG VIDEO_FPS
ENV VIDEO_FPS=${VIDEO_FPS}

ARG VIDEO_WIDTH
ENV VIDEO_WIDTH=${VIDEO_WIDTH}

ARG VIDEO_HEIGHT
ENV VIDEO_HEIGHT=${VIDEO_HEIGHT}

ARG VIDEO_DEVICE
ENV VIDEO_DEVICE=${VIDEO_DEVICE}

ARG VIDEO_FPS
ENV VIDEO_FPS=${VIDEO_FPS}

ARG VIDEO_RTSPPATH
ENV VIDEO_RTSPPATH=${VIDEO_RTSPPATH}

ENTRYPOINT [ "/bin/sh", "/start.sh" ]
