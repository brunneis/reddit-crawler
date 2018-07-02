#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, CircularOrderedSet
import random
import time
import crawler_helper as rch


class CommentCrawler(Link):

    def setup(self):
        self.spider_name = rch.get_spider_name('RCC')
        self.wait_seconds = 3 # Max waiting seconds between loops

    def _emit_retrieved(self, comment_body):
        self.queue.put(
            Electron(comment_body,
                     comment_body,
                     topic=self.output_topics[0]))

    def custom_input(self):
        while(True):
            for element in rch.get_all_comments_elements(self.spider_name,
                                                         items_no=100):
                comment_body = rch.get_comment_body(element)
                print(comment_body)
                self._emit_retrieved(comment_body)
            time.sleep(random.uniform(0, self.wait_seconds))


if __name__ == "__main__":
    CommentCrawler().start(link_mode=Link.CUSTOM_INPUT)
