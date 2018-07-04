#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, CircularOrderedSet
import crawler_helper as rch


class SubmissionExtractor(Link):

    def setup(self):
        self.spider_name = rch.get_spider_name('RSE')

    def transform(self, electron):
        submission_id = electron.value['submission_id']
        subreddit_id = electron.value['subreddit_id']

        submission = rch.get_submission_elements(self.spider_name,
                                                 subreddit_id,
                                                 submission_id)[0]
        submission_title = rch.get_submission_title(submission)
        submission_body = rch.get_submission_body(submission)

        electron = Electron(None,
                            {'title': submission_title,
                             'body': submission_body,
                             'type': 0})
        return electron


if __name__ == "__main__":
    SubmissionExtractor().start()
