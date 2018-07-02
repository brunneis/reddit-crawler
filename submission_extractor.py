#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, CircularOrderedSet
import crawler_helper as rch


class SubmissionExtractor(Link):
    def transform(self, electron):
        sumbission_id = electron.value['sumbission_id']
        subreddit_id = electron.value['subreddit_id']

        submission = rch.get_submission_elements(self.spider_name,
                                                 subreddit_id,
                                                 submission_id)[0]
        submission_title = rch.get_submission_title(submission)
        submission_body = rch.get_submission_body(submission)

        return Electron(None, {'title': submission_title, 'body': submission_body, 'type': 0})

if __name__ == "__main__":
    SubmissionExtractor().start()
