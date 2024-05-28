#!/bin/bash

jadio-podcast \
    ${BASE_URL} \
    /data/rss \
    --media-root /data/media \
    --database-host "mongodb://docker_mongo_1:27017/"
