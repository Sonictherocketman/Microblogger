# -*- coding: utf-8 -*-
""" A Python wrapper for the XML item elements.  """

from lxml.etree import Element
from lxml.builder import E

def post(data):
    """ Convert an lxml 'item' element to a dict representation.  """
    from dateutil.parser import parse
    item = _recursive_dict(data)
    if len(item) > 1:
        item[1]['pubdate'] = parse(item[1]['pubdate'])
        item[1]['pubdate_str'] = item[1]['pubdate'].strftime('%a, %d %b %Y %I:%M:%S')
        print item[1]
        return item[1]
    else:
        raise MalformedDataError


def to_element(data):
    """ Covert dict to lxml element. Only standard elements are inserted. If the
    post does not meet standards, raises MalformedDataError.
    See http://openmicroblog.com for information about the standard elements."""
    try:
        data = standardize(data)
    except MalformedDataError:
        print 'The post data provided does not meet Open Microblog standards. \n\
                Please see http://openmicroblog.com for information on required elements.'
        raise MalformedDataError

    # Check if the post is a reply.
    if data['is_reply']:
        return E.item(
                # General Info
                E.guid(data['guid']),
                E.pubDate(data['pubDate']),
                E.description(CDATA(data['description'])),
                E.language(data['language']),
                # Replying
                E.in_reply_to_status_id(data['in_reply_to_status_id']),
                E.in_reply_to_user_id(data['in_reply_to_user_id']),
                E.in_reply_to_user_link(data['in_reply_to_user_link'])
                )

    # Check if the post is a repost.
    elif data['is_repost']:
        return E.item(
                # General Info
                E.guid(data['guid']),
                E.pubDate(data['pubDate']),
                E.description(CDATA(data['description'])),
                E.language(data['language']),
                # Reposting
                E.reposted_status_id(data['reposted_status_id']),
                E.reposted_status_pubdate(data['reposted_status_pubdate']),
                E.reposted_status_user_id(data['reposted_status_user_id']),
                E.reposted_status_user_link(data['reposted_status_user_link'])
                )

    # Normal post.
    else:
        return E.item(
                # General Info
                E.guid(data['guid']),
                E.pubDate(data['pubDate']),
                E.description(CDATA(data['description'])),
                E.language(data['language'])
                )


def standardize(data):
    """ Checks the post and adds some metadata and appends any missing
    information with the defaults. If the post does not meet standards,
    raises MalformedDataError """

    # Check for normal post information.
    if 'guid' not in data.keys():
        raise MalformedDataError
    if 'pubDate' not in data.keys():
        raise MalformedDataError
    if 'description' not in data.keys():
        raise MalformedDataError

   # Check if its a repost. Make sure required info is present.
    if 'reposted_status_id' in data.keys():
        if 'reposted_status_pubdate' not in data.keys():
            raise MalformedDataError
        if 'reposted_status_user_id' not in data.keys():
            raise MalformedDataError
        if 'reposted_status_user_id' not in data.keys():
            raise MalformedDataError
        if 'reposted_status_user_link' not in data.keys():
            raise MalformedDataError
        data['is_repost'] = True

   # Check if its a reply. Make sure required info is present.
    elif 'in_reply_to_status_id' in data.keys():
        if 'in_reply_to_user_id' not in data.keys():
            raise MalformedDataError
        if 'in_reply_to_user_link' not in data.keys():
            raise MalformedDataError
        data['is_reply'] = True

    # Check for missing optional information.
    # Add default info if not provided.
    if 'language' not in data.keys():
        data['language'] = 'en'

    return data


def _recursive_dict(element):
    """ Converts an element to a recursive dict inside a tuple (tag, dict).
    From http://lxml.de/FAQ.html#how-can-i-map-an-xml-tree-into-a-dict-of-dicts """
    return element.tag, dict(map(_recursive_dict, element)) or element.text
