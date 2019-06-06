#!/bin/bash
LINKS_PATH=/opt/reddit-crawler
cd $LINKS_PATH

case "$1" in
    submission_crawler)
        LINK=submission_crawler.py
        ;;

    submission_extractor)
        LINK=submission_extractor.py
        ;;

    comment_crawler)
        LINK=comment_crawler.py
        ;;

    stats)
        LINK=stats.py
        ;;

    *)
        echo "Usage: [submission_crawler | submission_extractor | comment_crawler | stats] [ARGS]"
        exit 1
esac

shift
python $LINK "$@"
