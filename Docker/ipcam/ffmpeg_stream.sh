#!/bin/sh

echo STARTING FFMPEG STREAM
ffmpeg \
    -f v4l2 \
    -framerate ${VIDEO_FPS} \
    -re -stream_loop -1 \
    -video_size ${VIDEO_WIDTH}x${VIDEO_HEIGHT} \
    -input_format mjpeg \
    -i ${VIDEO_DEVICE} \
    -c copy \
    -f rtsp \
    rtsp://localhost:${VIDEO_RTSP_PORT}/${VIDEO_RTSP_PATH}

echo FFMPEG DONE KICKED THE BUCKET.
echo WAH WAH.
