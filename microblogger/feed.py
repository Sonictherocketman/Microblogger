class Feed():
    """ Contains the list of possible channel elements. Also a convenient object to represent the feeds.
    :see crawler:
    """
    all_elements = [
        'username',
        'user_id',
        'user_full_name',
        'description',
        'link',
        'relocate',
        'next_node',
        'blocks',
        'follows',
        'docs',
        'language',
        'lastBuildDate',
        'url',
        'reply_to_user',
        'reply_to_status',
        'reply_from_user_id',
        'reply_status_id',
        'user_link'
        'status_id',
        'pubdate',
        'description',
        'in_reply_to_status_id',
        'in_reply_to_user_id',
        'in_reply_to_user_link',
        'reposted_status_id',
        'reposted_status_pubdate',
        'reposted_status_user_id',
        'reposted_status_user_link'
    ]
    root_elements = [
        'username',
        'user_id',
        'user_full_name',
        'description',
        'link',
        'relocate',
        'next_node',
        'blocks',
        'follows',
        'docs',
        'language',
        'lastBuildDate'
    ]
    channel_elements = [
        'username',
        'user_id',
        'user_link',
        'user_full_name',
        'description',
        'link',
        'relocate',
        'next_node',
        'blocks',
        'follows',
        'reply_to',
        'docs',
        'language',
        'lastBuildDate',
        'item'
    ]
    item_elements = [
        'status_id',
        'pubdate',
        'description',
        'in_reply_to_status_id',
        'in_reply_to_user_id',
        'in_reply_to_user_link',
        'reposted_status_id',
        'reposted_status_pubdate',
        'reposted_status_user_id',
        'reposted_status_user_link'
    ]
    reply_to_elements = [
        'url',
        'reply_to_user',
        'reply_to_status',
        'reply_from_user_id',
        'reply_status_id',
        'user_link'
    ]

    def __init__(self, **entries):
        self.__dict__.update(entries)


