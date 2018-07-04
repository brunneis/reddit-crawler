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
        try:
            submission = rch.get_submission_elements(self.spider_name,
                                                     subreddit_id,
                                                     submission_id)[0]
        except IndexError:
            # Sometimes the prefix 'u_' is needed for the username
            submission = rch.get_submission_elements(self.spider_name,
                                                     'u_' + subreddit_id,
                                                     submission_id)[0]

        user_id = rch.get_user_id(submission)
        submission_title = rch.get_submission_title(submission)
        submission_body = rch.get_submission_body(submission)
        submission_timestamp = rch.get_submission_timestamp(submission)

        electron = Electron(None,
                            {'user_id': user_id,
                             'submission_id': submission_id,
                             'title': submission_title,
                             'body': submission_body,
                             'timestamp': submission_timestamp,
                             'subreddit_id': subreddit_id,
                             'type': 0})

        return electron


if __name__ == "__main__":
    SubmissionExtractor().start()
