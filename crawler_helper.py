#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from urllib.request import urlopen, Request
import gzip
import lxml.html
import traceback
import random
import logging
from lxml import etree
import dateutil.parser
import datetime
from datetime import timezone, timedelta
import re

# https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending
CHROME_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.5',
    'dnt': '1',
    'pragma': 'no-cache',
    'cache-control': 'no-control',
    'upgrade-insecure-requests': '1',
    'user-agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    'origin': 'https://www.reddit.com/'
}


# ITEMS #######################################################################
def get_user_id(element):
    try:
        return element.xpath("." + "/div[@class='entry unvoted']" + "/div[@class='tagline']" + "/span" +
                             "/a[contains(@class, 'author')]/text()")[0].encode('utf-8').decode('utf-8')
    # Post written by a deleted user
    except IndexError:
        return


def get_comment_user_id(element):
    try:
        return element.xpath("." + "/div[@class='entry unvoted']" + "/div[@class='tagline']" +
                             "/a[contains(@class, 'author')]/text()")[0].encode('utf-8').decode('utf-8')
    # Post written by a deleted user
    except IndexError:
        return


def get_comment_timestamp(element):
    # TODO revisar score hidden
    """ This function works only with a "thing" element of a given user_id
    submissions page (it does not work with a certain submission endpoint)
    """
    time_ago = element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[@class='tagline']"
        + "/text()[normalize-space()]")[0] \
        .replace("[score hidden]", "").strip()
    return _get_timestamp_from_text(time_ago)


def get_submission_timestamp(element):
    """ From the list of submissions page. It will fail sometimes from a
    given submission page
    """
    retrieved_datetime = element.xpath("." + "/div[@class='entry unvoted']" + "/div[@class='tagline']" + "/span" +
                                       "/time/@datetime")[0]
    # + "/time[@class='live-timestamp']")[0].attrib['datetime'])

    return int(dateutil.parser.parse(retrieved_datetime) \
        .replace(tzinfo=timezone.utc).timestamp())


def get_submission_id(element):
    """ This function works only with a "thing" element of a given user_id
    submissions page (it does not work with a certain submission endpoint)
    """
    return _get_id(element)


def get_subreddit_id(element, retrieve_user_if_not_subreddit=False):
    """ This function works only with a "thing" element of a given user_id
    submissions page (it does not work with a certain submission endpoint)
    """
    try:
        subreddit = element.xpath("." + "/div[@class='entry unvoted']" + "/div[@class='tagline']" + "/span" +
                                  "/a[contains(@class, 'subreddit')]/text()")[0]
        type, subreddit = subreddit.split('/')
        if type == 'r':
            return f'r/{subreddit}'
        # The text was posted to the user's profile (no subreddit)
        elif type == 'u' and retrieve_user_if_not_subreddit:
            return f'u/{subreddit}'
    except IndexError:
        return


def get_submission_title(element):
    """ List of submissions page
    """
    return element.xpath("." + "/div[@class='entry unvoted']" + "/p[@class='title']" + "/a[@class='may-blank']" +
                         "/text()")[0].encode('utf-8').decode('utf-8')


def get_content_url(element):
    """ Returns the URL of the posted content both internal or external links
    """
    return element.xpath("."
        + "/a[@class='title']"
        + "/@href")[0] \
        .split('.compact')[0]


def get_comment_url(element):
    return 'https://reddit.com' + element.xpath("." + "/div[@class='entry unvoted']" +
                                                "/div[@class='clear options_expando hidden']" + "/a" + "/@href")[1]


def get_submission_url(submission_id, subreddit_id):
    return f'https://www.reddit.com/{subreddit_id}/comments/{submission_id}/'


# def get_submission_url_from_comment_url(element):
#     return '/'.join(get_comment_url(element).split('/')[:-2]) + '/'


def get_submission_body(element):
    words = " ".join(text
                     for text in element.xpath("." + "/div[@class='expando']" + "/form[@class='usertext']" +
                                               "/div[@class='usertext-body']" + "/div[@class='md']//text()")).split()
    return " ".join(words)


def get_submission_score(element):
    return element.xpath("." + "/div[@class='entry unvoted']" + "/div[@class='tagline']" + "/span" +
                         "/span[@class='score unvoted']" + "/@title")[0]


def get_submission_no_comments(element):
    return element.xpath("." + "/div[@class='commentcount']" + "/a" + "/text()")[0].encode('utf-8').decode('utf-8')


def get_comment_id(element):
    return _get_id(element)


def get_comment_body(element):
    words = " ".join(text
                     for text in element.xpath("." + "/div[@class='entry unvoted']" + "/form[@class='usertext']" +
                                               "/div[@class='usertext-body']" + "/div[@class='md']//text()")).split()
    return " ".join(words)


def get_comment_subreddit_id(element):
    return 'r/' + element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[contains(@class, 'options_expando')]"
        + "/a"
        + "/@href")[1] \
        .split("/")[2]


def get_comment_submission_id(element):
    return element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[contains(@class, 'options_expando')]"
        + "/a"
        + "/@href")[1] \
        .split("/")[4]


def get_comment_submission_title(element):
    return element.xpath("." + "/a[@class='title']/text()")[0].encode('utf-8').decode('utf-8')


###############################################################################
def _get_id(element):
    return list(element.classes)[2].split('_')[1]


def _get_timestamp_from_text(time_ago):
    # datetime.today() with tzinfo None (UTC)
    estimated_datetime = datetime.datetime.today()
    if not re.match("just\snow.*", time_ago):
        m = re.match("([0-9]+)\s(h|mi|d|mo|y).+", time_ago)
        if m:
            time_groups = m.groups()
            if time_groups[1] is 'h':
                estimated_datetime = estimated_datetime \
                    - timedelta(hours=int(time_groups[0]))
            elif time_groups[1] is 'mi':
                estimated_datetime = estimated_datetime \
                    - timedelta(minutes=int(time_groups[0]))
            elif time_groups[1] is 'd':
                estimated_datetime = estimated_datetime \
                    - timedelta(days=int(time_groups[0]))
            elif time_groups[1] is 'mo':
                estimated_datetime = estimated_datetime \
                    - timedelta(days=int(time_groups[0]) * 30)
            elif time_groups[1] is 'y':
                estimated_datetime = estimated_datetime \
                    - timedelta(days=int(time_groups[0]) * 365)
        else:
            # print('DOES NOT MATCH: "' + time_ago + '"')
            return None
    return int(estimated_datetime.timestamp())


###############################################################################
def get_all_submissions_elements(spider_name, items_no=100):
    return get_subreddit_submissions_elements('r/all', spider_name, items_no)


def get_subreddit_submissions_elements(subreddit='r/all', spider_name=None, items_no=100):
    try:
        doc = _get_subreddit_submissions_lxml(subreddit, spider_name, items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except Exception as e:
        logging.warn(str(e))
        return []


def get_all_comments_elements(spider_name, items_no=100):
    return get_subreddit_comments_elements('r/all', spider_name, items_no)


def get_subreddit_comments_elements(subreddit='r/all', spider_name=None, items_no=100):
    try:
        doc = _get_subreddit_comments_lxml(subreddit, spider_name, items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except Exception as e:
        logging.warn(str(e))
        return []


def get_user_submissions_elements(spider_name, user_id, items_no=100):
    try:
        doc = _get_user_submissions_lxml(spider_name, user_id, items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except Exception as e:
        logging.warn(str(e))
        return []


def get_user_comments_elements(spider_name, user_id, items_no=100):
    try:
        doc = _get_user_comments_lxml(spider_name, user_id, items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except Exception as e:
        logging.warn(str(e))
        return []


def get_submission_elements(spider_name, subreddit_id, submission_id, items_no=500):
    """ Get all elements of a submission page (OP + comments) """
    try:
        doc = _get_submission_lxml(spider_name, subreddit_id, submission_id, items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except Exception as e:
        logging.warn(str(e))
        return []


def get_spider_name(crawler_name):
    # spider_name = crawler_name + "_test"
    spider_name = crawler_name + "_" \
       + "".join([str(random.randrange(10)) for i in range(5-1)])
    logging.info(spider_name)
    return spider_name


###############################################################################


def _get_subreddit_submissions_lxml(subreddit='r/all', spider_name=None, items_no=100):
    response = urlopen(_get_request(_get_subreddit_submissions_url(subreddit, items_no), spider_name))
    return _get_lxml_from_response(response)


def _get_subreddit_comments_lxml(subreddit='r/all', spider_name=None, items_no=100):
    response = urlopen(_get_request(_get_subreddit_comments_url(subreddit, items_no), spider_name))
    return _get_lxml_from_response(response)


def _get_user_submissions_lxml(spider_name, user_id, items_no=100):
    response = urlopen(_get_request(_get_user_submissions_url(user_id, items_no), spider_name))
    return _get_lxml_from_response(response)


def _get_user_comments_lxml(spider_name, user_id, items_no=100):
    response = urlopen(_get_request(_get_user_comments_url(user_id, items_no), spider_name))
    return _get_lxml_from_response(response)


def _get_submission_lxml(spider_name, subreddit_id, submission_id, items_no=500):
    response = urlopen(_get_request(_get_submission_url(subreddit_id, submission_id, items_no), spider_name))
    return _get_lxml_from_response(response)


###############################################################################
def _get_lxml_from_response(response):
    if response.info().get('Content-Encoding') == 'gzip':
        html_string = gzip.GzipFile(fileobj=response).read()
        return lxml.html.document_fromstring(html_string)


###############################################################################


def _get_subreddit_submissions_url(subreddit='r/all', items_no=100, sort='new'):
    url = f'https://www.reddit.com/{subreddit}/{sort}/.compact?limit={items_no}'
    return url


def _get_subreddit_comments_url(subreddit='r/all', items_no=100):
    url = f'https://www.reddit.com/{subreddit}/comments/.compact?limit={items_no}'
    return url


def _get_user_submissions_url(user_id, items_no=100):
    url = ('https://www.reddit.com/user/' + user_id + '/submitted/.compact?limit=' + str(items_no))
    return url


def _get_submission_url(subreddit_id, submission_id, items_no=500):
    url = ('https://www.reddit.com/' + subreddit_id + '/comments/' + submission_id + '/.compact?limit=' + str(items_no))
    return url


def _get_user_comments_url(user_id, items_no=100):
    url = ('https://www.reddit.com/user/' + user_id + '/comments/.compact?limit=' + str(items_no))
    return url


def _get_request(url, spider_name):
    return Request(url=url, data=None, headers=CHROME_HEADERS)