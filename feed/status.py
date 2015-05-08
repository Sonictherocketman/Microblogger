""" A model for a user's post. """


from dateutil.parser import parse

def _enum(**enums):
    return type('Enum', (), enums)


DATE_STR_FORMAT = '%a, %d %b %Y %H:%M:%S %z'

# Status Model


StatusType = _enum(
        STATUS=0,
        REPLY=1,
        REPOST=2
        )


class Status(object):
    """ This class models a given post from a user.

    @author Brian Schrader
    @since 2015-05-03
    """

    def __init__(self, entries, status_type=None):
        self.__dict__.update(**entries)
        self.status_type = status_type if status_type is not None \
                else self._determine_status_type()
        self.pubdate = parse(entries.get('pubdate'))

    def to_element(self):
        """ Covert dict to lxml element. Only standard elements are inserted. If the
        post does not meet standards, raises AttributeError.
        See http://openmicroblog.com for information about the standard elements."""
        if self.is_standard:
            self = standardize(self)
        else:
            print 'The post self provided does not meet Open Microblog standards. \n\
                    Please see http://openmicroblog.com for information on required elements.'
            raise AttributeError

        if self.status_type == StatusType.REPLY:
            return E.item(
                    # General Info
                    E.guid(self.guid),
                    E.pubdate(self.pubdate.strftime(DATE_STR_FORMAT)),
                    E.description(self.description),
                    E.language(self.language),
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
                    E.language(self.language)
                    )

    def is_standard(self):
        """ Checks the post and adds some metadata and appends any missing
        information with the defaults. If the post does not meet standards
        returns False else True. """

        try:
            getattr(self, 'guid')
            getattr(self, 'pubdate')
            getattr(self, 'description')
        except Exception as e:
            return False
        print self.status_type
        if self.status_type == StatusType.REPOST:
            try:
                getattr(self, 'reposted_status_pubdate')
                getattr(self, 'reposted_status_user_id')
                getattr(self, 'reposted_status_id')
                getattr(self, 'reposted_status_user_link')
            except Exception as e:
                print e
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
        # TODO May not find some cases.
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
