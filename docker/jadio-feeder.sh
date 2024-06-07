#!/bin/bash

jadio-feeder update-feeds \
    --base-url=${BASE_URL} \
    --rss-root=/data/rss \
    --media-root=/data/media \
    --database-host="mongodb://docker-mongo-1:27017/"
