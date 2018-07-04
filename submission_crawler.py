#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, CircularOrderedSet
import random
import time
import crawler_helper as rch


class SubmissionCrawler(Link):

    def setup(self):
        self.spider_name = rch.get_spider_name('RSC')
        self.processed_ids = CircularOrderedSet(1000)
        self.wait_seconds = 3 # Max waiting seconds between loops

    def _emit_retrieved(self, value):
        electron = Electron(None, value, topic=self.output_topics[0])
        self.queue.put(electron)

    def custom_input(self):
        while(True):
            for element in rch.get_all_submissions_elements(self.spider_name,
                                                            items_no=100):
                submission_id = rch.get_submission_id(element)
                if submission_id in self.processed_ids:
                    continue
                self.processed_ids.add(submission_id)
                subreddit_id = rch.get_subreddit_id(element)

                self._emit_retrieved({'submission_id': submission_id,
                                      'subreddit_id': subreddit_id})

            time.sleep(random.uniform(0, self.wait_seconds))


if __name__ == "__main__":
    SubmissionCrawler().start(link_mode=Link.CUSTOM_INPUT)
