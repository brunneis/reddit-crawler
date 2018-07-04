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


# ITEMS #######################################################################
def get_user_id(element):
    try:
        return str(element.xpath("."
            + "/div[@class='entry unvoted']"
            + "/div[@class='tagline']"
            + "/span"
            + "/a[contains(@class, 'author')]/text()")[0])
    except IndexError:
        pass

def get_user_id_from_subreddit(element):
    try:
        return str(element.xpath("."
            + "/div[@class='entry unvoted']"
            + "/div[@class='tagline']"
            + "/a[contains(@class, 'author')]/text()")[0])
    except IndexError:
        pass

def get_comment_timestamp(element):
    """ This function works only with a "thing" element of a given user_id
    submissions page (it does not work with a certain submission endpoint)
    """
    time_ago = str(element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[@class='tagline']"
        + "/text()[normalize-space()]")[0]) \
        .replace("[score hidden]", "").strip()
    return _get_timestamp_from_text(time_ago)

def get_submission_timestamp(element):
    """ This function works only with a "thing" element of a given user_id
    submissions page (it does not work with a certain submission endpoint)
    """
    retrieved_datetime = str(element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[@class='tagline']"
        + "/span"
        + "/time/@datetime")[0])
        # + "/time[@class='live-timestamp']")[0].attrib['datetime'])

    return int(dateutil.parser.parse(retrieved_datetime) \
        .replace(tzinfo=timezone.utc).timestamp())

def get_submission_id(element):
    """ This function works only with a "thing" element of a given user_id
    submissions page (it does not work with a certain submission endpoint)
    """
    return _get_id(element)

def get_subreddit_id(element):
    """ This function works only with a "thing" element of a given user_id
    submissions page (it does not work with a certain submission endpoint)
    """
    return str(element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[@class='tagline']"
        + "/span"
        + "/a[contains(@class, 'subreddit')]/text()")[0].split('/')[1])

def get_submission_title(element):
    return str(element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/p[@class='title']"
        + "/a[@class='may-blank']/text()")[0])

def get_submission_body(element):
    words = " ".join(str(text) for text in element.xpath("."
        + "/div[@class='expando']"
        + "/form[@class='usertext']"
        + "/div[@class='usertext-body']"
        + "/div[@class='md']//text()")).split()
    return " ".join(words)

def get_comment_id(element):
    return _get_id(element)

def get_comment_body(element):
    words = " ".join(str(text) for text in element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/form[@class='usertext']"
        + "/div[@class='usertext-body']"
        + "/div[@class='md']//text()")).split()
    return " ".join(words)

def get_comment_subreddit_id(element):
    return str(element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[contains(@class, 'options_expando')]"
        + "/a"
        + "/@href")[1]).split("/")[2]

def get_comment_submission_id(element):
    return str(element.xpath("."
        + "/div[@class='entry unvoted']"
        + "/div[contains(@class, 'options_expando')]"
        + "/a"
        + "/@href")[1]).split("/")[4]

def get_comment_submission_title(element):
    return str(element.xpath("."
        + "/a[@class='title']/text()")[0])

###############################################################################
def _get_id(element):
    return str((list(element.classes)[2].split('_')[1]))

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
    try:
        doc = _get_all_submissions_lxml(spider_name, items_no=items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except:
        return []

def get_all_comments_elements(spider_name, items_no=100):
    try:
        doc = _get_all_comments_lxml(spider_name, items_no=items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except:
        return []

def get_user_submissions_elements(spider_name, user_id,
    items_no=100):
    try:
        doc = _get_user_submissions_lxml(spider_name,
                                         user_id,
                                         items_no=items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except:
        return []

def get_user_comments_elements(spider_name, user_id,
    items_no=100):
    try:
        doc = _get_user_comments_lxml(spider_name,
                                      user_id,
                                      items_no=items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except:
        return []

def get_submission_elements(spider_name, subreddit_id, submission_id,
    items_no=500):
    """ Get all elements of a submission page (OP + comments) """
    try:
        doc = _get_submission_lxml(spider_name,
                                   subreddit_id,
                                   submission_id,
                                   items_no=items_no)
        return doc.xpath("//div[contains(@class, 'thing')]")
    except urllib.error.HTTPError:
        return []

def get_spider_name(crawler_name):
    # spider_name = crawler_name + "_test"
    spider_name = crawler_name + "_" \
       + "".join([str(random.randrange(10)) for i in range(5-1)])
    print(spider_name)
    return spider_name

###############################################################################
def _get_all_submissions_lxml(spider_name, items_no=100):
    response = urlopen(_get_request(
        _get_all_submissions_url(items_no=items_no),
        spider_name))
    return _get_lxml_from_response(response)

def _get_all_comments_lxml(spider_name, items_no=100):
    response = urlopen(_get_request(
        _get_all_comments_url(items_no=items_no),
        spider_name))
    return _get_lxml_from_response(response)

def _get_user_submissions_lxml(spider_name, user_id,
    items_no=100):
    response = urlopen(_get_request(
        _get_user_submissions_url(user_id,
                                  items_no=items_no),
        spider_name))
    return _get_lxml_from_response(response)

def _get_user_comments_lxml(spider_name, user_id,
    items_no=100):
    response = urlopen(_get_request(
        _get_user_comments_url(user_id,
                               items_no=items_no),
        spider_name))
    return _get_lxml_from_response(response)

def _get_submission_lxml(spider_name, subreddit_id, submission_id,
    items_no=500):
    response = urlopen(_get_request(
        _get_submission_url(subreddit_id,
                            submission_id,
                            items_no=items_no),
        spider_name))
    return _get_lxml_from_response(response)

###############################################################################
def _get_lxml_from_response(response):
    if response.info().get('Content-Encoding') == 'gzip':
        f = gzip.GzipFile(fileobj=response)
        return lxml.html.document_fromstring(f.read())

###############################################################################
def _get_all_submissions_url(items_no=100, do_print=False):
    url = 'https://www.reddit.com/r/all/new/.compact?limit=' + str(items_no)
    if do_print:
        logging.info(url)
    return url

def _get_all_comments_url(items_no=100, do_print=False):
    url = 'https://www.reddit.com/r/all/comments/.compact?limit=' + str(items_no)
    if do_print:
        logging.info(url)
    return url

def _get_user_submissions_url(user_id, items_no=100, do_print=False):
    url = ('https://www.reddit.com/user/'
        + user_id
        + '/submitted/.compact?limit=' + str(items_no))
    if do_print:
        logging.info(url)
    return url

def _get_submission_url(subreddit_id, submission_id,
                        items_no=500, do_print=False):
    url = ('https://www.reddit.com/r/'
        + subreddit_id
        + '/comments/'
        + submission_id
        + '/.compact?limit=' + str(items_no))
    if do_print:
        logging.info(url)
    return url

def _get_user_comments_url(user_id, items_no=100, do_print=False):
    url = ('https://www.reddit.com/user/'
        + user_id
        + '/comments/.compact?limit=' + str(items_no))
    if do_print:
        logging.info(url)
    return url

def _get_request(url, spider_name):
    request = Request(
        url=url,
        data=None,
        headers={
            'user-agent': 'Mozilla/5.0 ' + spider_name + ' (Linux; en)',
            'accept-language': 'en-US,en;q=0.8,gl;q=0.6,es;q=0.4,pt;q=0.2',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'dnt': '1',
            'upgrade-insecure-requests': '1'
        }
    )
    return request
