"""
A recursive Microblog feed parser. Point it at a URL, or give it some text, and watch it go.
"""

import re
from feed import Feed


def crawl_and_parse(url=None, text=None, element_found_callback=None):
    """ Crawls the given URL _or_ text yielding an object representing the feed.w
    :returns Feed
    """
    # Some checks.
    if not hasattr(element_found_callback, '__call__'):
        print 'The callback you provided is not callable.'
        raise TypeError

    # Get the data from the URL.
    parse_me = ''
    if url is not None:
        import urllib2
        response = urllib2.urlopen(url)
        if response is not None:
            parse_me = response.read()

    # Get the data from the string provided.
    elif text is not None:
        parse_me = text

    # Nothing provided to parse.
    else:
        print 'No URL or string provided.'
        return

    # Extract the channel.
    channel_pattern = re.compile(pattern=r'<channel>(.+?)</channel>', flags=re.UNICODE | re.IGNORECASE | re.DOTALL)
    try:
        channel = re.search(pattern=channel_pattern, string=parse_me).group(1)
    except AttributeError:
        print 'No channel elements found.'
        return

    # Scan for the root channel elements.
    return recursive_crawl(channel, element_found_callback)


def recursive_crawl(xml_feed, element_found_callback):
    """ Parses the XML provided. Stops when there are no more child elements, or <![CDATA[]> tags are present.
    Should not parse XML/HTML inside those tags.
    :param xml_feed:
    :param element_found_callback:
    :returns Feed:
    """
    feed = {}
    flags = re.UNICODE | re.IGNORECASE | re.DOTALL
    for element_name in Feed.all_elements:
        for result in re.finditer(pattern='<\w?+?{0}\w?+?>(.+)<\w?+?/{0}\w?+?>'.format(element_name),
                                  string=xml_feed,
                                  flags=flags):
            if result:
                element_contents = result.group(1).lower()
                if element_found_callback is not None:
                    # Call the callback...
                    element_found_callback(element_name, element_contents)

                # Determine whether or not to go on.
                # Go on if inside elements are detected,
                # Do not if no tags found or if only remaining tags are inside <![CDATA[]> tags.
                if any(True for element in Feed.all_elements if element in element_contents):
                    if any(True for i in re.findall(pattern=r'<{0}>\w?+?<!\[CDATA\[.+\]>'.format(element_name),
                                                    string=element_contents,
                                                    flags=flags)):
                        # <![CDATA[]> Tags found, extract the text.
                        feed[element_name] = re.findall(pattern=r'<!\[CDATA\[(.+)\]\]',
                                                        string=element_contents,
                                                        flags=re.DOTALL)[0]
                    else:
                        # Go deeper.
                        feed[element_name] = recursive_crawl(element_contents, element_found_callback)
                else:
                    # There are no deeper tags. Just use the element content.
                    feed[element_name] = element_contents

    # Return a Feed object modeled after the dict created.
    return Feed(**feed)

