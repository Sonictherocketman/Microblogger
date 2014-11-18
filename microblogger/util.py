""" Utilities for doing basic feed file IO.  """

from lxml.etree import etree

# TODO
# - Add pagination support for reading and writing.

def get_user_feed(rel_location):
    """ Get the etree representation of the feed located at the rel_location.  """
    tree = None
    with open(rel_location, 'r') as f:
        data = f.read()
        tree = etree.parse(StringIO(data))
    return tree


def write_user_feed(tree, rel_location)
    """ Write the etree representation of the feed to the rel_locaiton.  """
    with open(rel_location, 'w') as f:
        tree.write(f)

