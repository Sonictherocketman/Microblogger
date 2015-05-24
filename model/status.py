""" A model for a user's post. """

from dateutil.parser import parse
from lxml.builder import E
from lxml.etree import CDATA
from datetime import datetime
from pytz import timezone

def _enum(**enums):
    return type('Enum', (), enums)


DATE_STR_FORMAT = '%a, %d %b %Y %H:%M:%S %z'
READABLE_DATE_STR_FORMAT = '%m/%d/%Y %H:%M'

# Status Model


StatusType = _enum(
        STATUS=0,
        REPLY=1,
        REPOST=2
        )

class StatusNotStandardError(Exception):
    """ Occurs when an element is attempting to be written
    as an element to lxml, but the given status does not
    meet the standard.
    """
    pass


class Status(object):
    """ This class models a given post from a user.

    @author Brian Schrader
    @since 2015-05-03
    """

    def __init__(self, entries, user=None, status_type=None):
        self.__dict__.update(**entries)
        self.status_type = status_type if status_type is not None \
                else self._determine_status_type()
        if isinstance(entries.get('pubdate'), datetime):
            self.pubdate = entries.get('pubdate')
        else:
            self.pubdate = parse(entries.get('pubdate'))
        tz = timezone('US/Pacific')
        self.readable_pubdate = self.pubdate.astimezone(tz)\
                .strftime(READABLE_DATE_STR_FORMAT)

        if self.status_type == StatusType.REPOST:
            self.reposted_status_pubdate = parse(self.reposted_status_pubdate)
        self.user = user

    def to_element(self):
        """ Covert dict to lxml element. Only standard elements are inserted. If the
        post does not meet standards, raises AttributeError.
        See http://openmicroblog.com for information about the standard elements."""
        if not self.is_standard():
            raise StatusNotStandardError('Status does not meet the Open Microblog Standard')

        if self.status_type == StatusType.REPLY:
            return E.item(
                    # General Info
                    E.guid(self.guid),
                    E.pubdate(self.pubdate.strftime(DATE_STR_FORMAT)),
                    E.description(self.description),
                    E.language(self.language),
                    E.reply(self.reply),
                    # Replying
                    E.in_reply_to_status_id(self.in_reply_to_status_id),
                    E.in_reply_to_user_id(self.in_reply_to_user_id),
                    E.in_reply_to_user_link(self.in_reply_to_user_link)
                    )
        elif self.status_type == StatusType.REPOST:
            return E.item(
                    # General Info
                    E.guid(self.guid),
                    E.pubdate(self.pubdate.strftime(DATE_STR_FORMAT)),
                    E.description(self.description),
                    E.language(self.language),
                    E.reply(self.reply),
                    # Reposting
                    E.reposted_status_id(self.reposted_status_id),
                    E.reposted_status_pubdate(self.reposted_status_pubdate.strftime(DATE_STR_FORMAT)),
                    E.reposted_status_user_id(self.reposted_status_user_id),
                    E.reposted_status_user_link(self.reposted_status_user_link)
                    )
        else:
            return E.item(
                    # General Info
                    E.guid(self.guid),
                    E.pubdate(self.pubdate.strftime(DATE_STR_FORMAT)),
                    E.description(self.description),
                    E.language(self.language),
                    E.reply(self.reply)
                    )

    def is_standard(self):
        """ Checks the post and adds some metadata and appends any missing
        information with the defaults. If the post does not meet standards
        returns False else True. """

        try:
            getattr(self, 'guid')
            getattr(self, 'pubdate')
            getattr(self, 'description')
            getattr(self, 'reply')
        except Exception as e:
            return False
        if self.status_type == StatusType.REPOST:
            try:
                getattr(self, 'reposted_status_pubdate')
                getattr(self, 'reposted_status_user_id')
                getattr(self, 'reposted_status_id')
                getattr(self, 'reposted_status_user_link')
            except Exception as e:
                return False
        elif self.status_type == StatusType.REPLY:
            try:
                getattr(self, 'in_reply_to_status_id')
                getattr(self, 'in_reply_to_user_id')
                getattr(self, 'in_reply_to_user_link')
            except Exception as e:
                return False
        try:
            getattr(self, 'language')
        except Exception as e:
            self.language = 'en'

        return True

    def _determine_status_type(self):
        # TODO May not accurately
        status_type = None
        try:
            getattr(self, 'reposted_status_pubdate')
            getattr(self, 'reposted_status_user_id')
            getattr(self, 'reposted_status_id')
            getattr(self, 'reposted_status_user_link')
            status_type = StatusType.REPOST
        except Exception as e:
            try:
                getattr(self, 'in_reply_to_status_id')
                getattr(self, 'in_reply_to_user_id')
                getattr(self, 'in_reply_to_user_link')
                status_type = StatusType.REPLY
            except Exception as e:
                status_type = StatusType.STATUS
        return status_type


def _recursive_dict(element):
    """ Converts an element to a recursive dict inside a tuple (tag, dict).
    From http://lxml.de/FAQ.html#how-can-i-map-an-xml-tree-into-a-dict-of-dicts """
    return element.tag, dict(map(_recursive_dict, element)) or element.text