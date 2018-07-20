#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, CircularOrderedSet
import random
import time
import crawler_helper as rch


class CommentCrawler(Link):

    def setup(self):
        self.spider_name = rch.get_spider_name('RCC')
        self.processed_ids = CircularOrderedSet(1000)
        self.wait_seconds = 3 # Max waiting seconds between loops

    def _emit_retrieved(self, value):
        electron = Electron(None, value, topic=self.output_topics[0])
        self.queue.put(electron)

    def custom_input(self):
        while(True):
            for element in rch.get_all_comments_elements(self.spider_name,
                                                         items_no=100):
                comment_id = rch.get_comment_id(element)
                if comment_id in self.processed_ids:
                    continue
                self.processed_ids.add(comment_id)

                user_id = rch.get_user_id_from_subreddit(element)
                comment_timestamp = rch.get_comment_timestamp(element)
                comment_body = rch.get_comment_body(element)
                submission_id = rch.get_comment_submission_id(element)
                submission_title = rch.get_comment_submission_title(element)
                subreddit_id = rch.get_comment_subreddit_id(element)

                self._emit_retrieved({'user_id': user_id,
                                      'comment_id': comment_id,
                                      'body': comment_body,
                                      'timestamp': comment_timestamp,
                                      'submission_id': submission_id,
                                      'submission_title': submission_title,
                                      'subreddit_id': subreddit_id,
                                      'type': 1})

            time.sleep(random.uniform(0, self.wait_seconds))


if __name__ == "__main__":
    CommentCrawler().start(link_mode=Link.CUSTOM_INPUT)
