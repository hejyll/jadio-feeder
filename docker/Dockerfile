FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    git \
    python3 \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN python3 -m pip install git+https://github.com/hejyll/jadio-feeder

COPY ./jadio-feeder.sh /etc/cron.daily/jadio-feeder
RUN ln -sf /proc/1/fd/1 /var/log/cron.log

CMD cron -f
