#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, CircularOrderedSet
import crawler_helper as rch
import logging


class SubmissionExtractor(Link):
    def setup(self):
        self.spider_name = rch.get_spider_name('RSE')

    def transform(self, electron):
        submission_id = electron.value['submission_id']
        subreddit_id = electron.value['subreddit_id']

        submissions = rch.get_submission_elements(self.spider_name, subreddit_id, submission_id)
        if not submissions:
            return
        submission = submissions[0]

        body = rch.get_submission_body(submission)
        url = rch.get_submission_url(submission_id, subreddit_id)

        electron.value['body'] = body
        electron.value['url'] = url
        electron.value['type'] = 0
        electron.value['src'] = 'reddit'

        logging.info(electron.value)

        return electron


if __name__ == "__main__":
    SubmissionExtractor().start()
