#!/bin/bash
LINKS_PATH=/opt/reddit-crawler
cd $LINKS_PATH

case "$1" in
    submission_crawler)
        LINK=submission_crawler.py
        ;;

    comment_crawler)
        LINK=comment_crawler.py
        ;;

    *)
        echo "Usage: [submission_crawler | comment_crawler] [ARGS]"
        exit 1
esac

shift
python $LINK "$@"
