#!/bin/bash
DATA_PATH=$(cat DATA_PATH)/kafka

./build.sh
docker rm -f kafka submission_crawler submission_extractor comment_crawler 2> /dev/null

docker run --restart unless-stopped -d --net=host  \
-v $DATA_PATH:/opt/kafka/default/logs \
--ulimit nofile=90000:90000 \
--name kafka \
catenae/kafka

docker run -d --restart unless-stopped --net=host --name submission_crawler \
brunneis/reddit-crawler submission_crawler \
-o submission_ids \
-b 127.0.0.1:9092

docker run -d --restart unless-stopped --net=host --name submission_extractor \
brunneis/reddit-crawler submission_extractor \
-i submission_ids \
-o new_texts \
-b 127.0.0.1:9092

#docker run -d --restart unless-stopped --net=host --name comment_crawler \
#brunneis/reddit-crawler comment_crawler \
#-o new_texts \
#-b 127.0.0.1:9092
