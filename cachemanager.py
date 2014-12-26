""" Manages the CRUD of the app cache.

The app cache can store a number of things:
    - the main user's timeline (the most
        recent 1000 posts)
    - posts (by other users)
    - users
    - images (TODO)

For all methodss, the cache will return None,
if no results were found or if there was a
problem.
"""

class CacheManager():

    # Init/Destroy

    def __init__(self, cache_location=None):
        """ Default contructor. Passing cache_location will
        create a cache at that location just like create_cache. """
        if cache_location is not None:
            self.create_cache(cache_location)

    def create_cache(location):
        """ Creates a cache at the given location. If the cache already
        exists, then it clears it. """
        # TODO
        pass

    def destroy_cache():
        """ Destroys the stored cache. The file will be deleted. """
        # TODO
        pass

    # Main User's Timeline Functions

    def get_timeline(self):
        """ Retrieves the main user's cached timeline. """
        # TODO
        pass

    def add_to_timeline(self, post):
        """ Caches the given post in the user's
        timeline. """
        # TODO
        pass

    def remove_from_timeline(self, post_id):
        """ Removes the post with the given post_id
        from the user's cached timeline. """
        # TODO
        pass



