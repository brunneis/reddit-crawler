#!/bin/bash
DATA_PATH=$(cat DATA_PATH)/kafka

docker rm -f kafka comment_crawler # submission_crawler

docker run --restart unless-stopped -d --net=host  \
-v $DATA_PATH:/opt/kafka/default/logs \
--ulimit nofile=90000:90000 \
--name kafka \
catenae/kafka

./build.sh

# docker run -d --restart unless-stopped --net=host --name submission_crawler \
# --cpuset-cpus="$1" \
# brunneis/reddit-crawler submission_crawler \
# -o new_texts \
# -b 127.0.0.1:9092

docker run -d --restart unless-stopped --net=host --name comment_crawler \
--cpuset-cpus="$1" \
brunneis/reddit-crawler comment_crawler \
-o new_texts \
-b 127.0.0.1:9092
