""" Manages the CRUD of the app's settings. """


import os, json
from util import to_settings, from_settings


class SettingsManager():

    # Class Variables
    settings_file_location = os.path.expanduser('~/.microblogger_settings.json')

    # Init/Destroy

    def __init__(self, settings_file_location=None):
        """ Default contructor. Passing settings_file_location will
        create a settings configuration, if one does not already exist, at
        that location. """

        SettingsManager.settings_file_location = settings_file_location

        # Create a settings file if one does not already exist.
        if settings_file_location is not None and \
                not os.path.isfile(settings_file_location):
            SettingsManager.create_settings(settings_file_location)

    @staticmethod
    def create_settings(location):
        """ Creates a settings configuration at the given location.
        If the configuration already exists, then it clears it. """
        SettingsManager.settings_file_location = location

        # Write the empty settings file.
        data = {}
        with open(SettingsManager.settings_file_location, 'w') as f:
            f.write(json.dumps(data))

    @staticmethod
    def destroy_settings():
        """ Destroys the stored settings configuration. The file will be deleted. """
        # TODO
        pass

    @staticmethod
    def clear_settings():
        """ Clears the settings. All files remain. """
        # TODO
        pass

    @staticmethod
    def add(key, value):
        """ Adds the given value to the settings file. """
        return to_settings(SettingsManager.settings_file_location, key, value)

    @staticmethod
    def get(key):
        """ Gets the value for the given key from the settings. """
        return from_settings(SettingsManager.settings_file_location, key)

    @staticmethod
    def get_user(user_id):
        return SettingsManager.get('registered_users')[user_id]

    @staticmethod
    def add_user(username, pwd_hash, user_id, feed_location, blocks_location, follows_location):
        users = SettingsManager.get('registered_users')
        if users is None:
            users = {}
        users[user_id] = {
                'pwd_hash': pwd_hash,
                'username': username,
                'feed_location': feed_location,
                'blocks_location': blocks_location,
                'follows_location': follows_location
                }
        SettingsManager.add('registered_users', users)




