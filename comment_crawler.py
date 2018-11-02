#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, CircularOrderedSet
import random
import time
import crawler_helper as rch
import logging


class CommentCrawler(Link):

    def setup(self):
        self.spider_name = rch.get_spider_name('RCC')
        self.processed_ids = CircularOrderedSet(1000)
        self.wait_seconds = 3 # Max waiting seconds between loops

    def generator(self):
        while(True):
            for comment in rch.get_all_comments_elements(self.spider_name,
                                                         items_no=100):
                comment_id = rch.get_comment_id(comment)
                if comment_id in self.processed_ids:
                    continue
                self.processed_ids.add(comment_id)

                user_id = rch.get_comment_user_id(comment)
                comment_timestamp = rch.get_comment_timestamp(comment)
                comment_body = rch.get_comment_body(comment)
                submission_id = rch.get_comment_submission_id(comment)
                submission_title = rch.get_comment_submission_title(comment)
                subreddit_id = rch.get_comment_subreddit_id(comment)
                comment_url = rch.get_comment_url(comment)
                submission_url = rch.get_submission_url(submission_id, subreddit_id)

                electron = Electron(None,
                                    {'user_id': user_id,
                                     'comment_id': comment_id,
                                     'body': comment_body,
                                     'timestamp': comment_timestamp,
                                     'comment_url': comment_url,
                                     'submission_id': submission_id,
                                     'submission_title': submission_title,
                                     'subreddit_id': subreddit_id,
                                     'submission_url': submission_url,
                                     'type': 1,
                                     'src': 'reddit'},
                                    topic=self.output_topics[0])
                logging.info(electron.value)
                self.send(electron)
            time.sleep(random.uniform(0, self.wait_seconds))


if __name__ == "__main__":
    CommentCrawler().start(link_mode=Link.CUSTOM_INPUT)
