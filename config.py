# -*- coding: utf-8 -*-
#!/usr/local/bin/python

""" Configuration script for microblogger.

    Running this script will:
    - Generate and prepopulate the server settings
    - Create and setup the Caching
    - Generate and give directions for installing microblogger on Apache.
    - Syntax check apache and rollback changes if it breaks anything.
    - Install the crontab script for automatically running the crawler.
"""

from settingsmanager import SettingsManager
from cachemanager import CacheManager
import os
import sys
import signal
import pwd
from crontab import CronTab

## TODO
# - Add duplication protection to the Apache conf writer.
# - Make the apachecktl ouput pretty.
# - Fix so no sudo is required.
# - Add crawler setup.
# - Fix the .settings file to be installed under the microblogger user not the installing user.
##

# Configuration
CACHE = '/tmp/microblog/'
SETTINGS = os.path.expanduser('~/.microblogger_settings.json')
ROOT_DIR = '/var/www/microblogger/'
DEFAULT_TIMELINE_SIZE = 25
MAX_FILE_SIZE_BYTES = 500000
MAX_POSTS_PER_FEED = 500


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():

    os.system('cls' if os.name == 'nt' else 'clear')
    print '''
    =========================================
    {0}Welcome to Microblogger{1}
    =========================================
    This installer will guide you through configuring your new Microblogger.
    The installation has 2 short parts:
    - Apache setup (for the website)
    - Crawler setup (for the ability to read other people's feeds)

    Microblogger runs on Apache. To install Microblogger on anything else,
    you will need to manually install and configure the service.

    Before beginning, please create a new user for Microblogger to run under.
    For security reasons, Apache will run Microblogger under a different user.

    In Linux, this can be done by following the instructions here:

    http://www.cyberciti.biz/faq/howto-add-new-linux-user-account/

    Have you already done this? (y/N)
    '''.format(bcolors.HEADER, bcolors.ENDC)
    ans = raw_input('>>')
    if 'y' not in ans.lower():
        print '''
    Please complete this step and try again.
        '''
        sys.exit()

    print '''
    Configuring...
    Creating caches...
    '''

    # Get everything going.
    CacheManager.create_cache(CACHE)
    SettingsManager(SETTINGS)

    SettingsManager.add('default_timeline_size', DEFAULT_TIMELINE_SIZE)
    SettingsManager.add('max_feed_size_bytes', MAX_FILE_SIZE_BYTES)
    SettingsManager.add('max_posts_per_feed', MAX_POSTS_PER_FEED)

    # Create a secret key.
    SettingsManager.add('secret', os.urandom(64).encode('base-64'))

    print '    {0}OK{1}'.format(bcolors.OKGREEN, bcolors.ENDC)

    # Apache config.
    print '''
    =========================================
    {0}Microblog User Setup{1}
    =========================================
    Microblog user (Linux user, created above):
    '''.format(bcolors.HEADER, bcolors.ENDC)
    user = raw_input('>>')
    while not validate_user(user):
        print '''
    {0}[Error]{1} Please input a valid username.
    '''.format(bcolors.FAIL, bcolors.ENDC)
        user = raw_input('>>')
    print '''
    =========================================
    {0}Automatic Apache Installation{1}
    =========================================
    Use default web location? (y/N)

    i.e. {2}
    '''.format(bcolors.HEADER, bcolors.ENDC, ROOT_DIR)
    defaults = raw_input('>>')
    location = ''
    if 'n' in defaults.lower():
        print '''
    File paths must already exist, and be accessable to Apache.
    Paths should be in the form /path/to/web/location.

    The path should also be a directory.

    Plese input the location:'''
        location = raw_input('>>')
        while not os.path.exists(location) and os.path.isdir(location):
            print 'Path is not valid. Enter a valid path.'
            location = raw_input('Location: ')
    else:
        location = ROOT_DIR
    # Append the trailing /
    if not location[-1] == '/':
        location + '/'

    # Get the admin info.
    print '''
    What email address can we send errors to?
    '''
    email = raw_input('>>')
    print '''
    What is the desired server name?
    i.e. microblog.mydomain.com
    '''
    domain = raw_input('>>')

    # Create the custom Apache conf.
    conf = ''
    with open('bin/httpd.conf-addition', 'r') as f:
        conf = f.read()
    conf = conf.replace('{{WSGI_USER}}', user)\
            .replace('{{WSGI_DIR}}', location)\
            .replace('{{WSGI_FILE_LOCATION}}', location + 'microblogger.wsgi')\
            .replace('{{ADMIN_EMAIL}}', email)\
            .replace('{{SERVER_NAME}}', domain)

    print '''
    Do you want to automatically install the Apache configuration? (y/N)
    (Manual install is reccommended for systems with lots of custom
    Apache configurations)'''
    ans = raw_input('>>')

    if 'y' not in ans.lower():
        print_manual_conf(conf)
        sys.exit()
    else:
        # Write the apache conf to file.
        print '''
    Is your Apache conf file in the default location
    (i.e. /etc/httpd/conf/httpd.conf)? (y/N)
        '''
        ans = raw_input('>>')
        httpd_location = '/etc/httpd/conf/httpd.conf'
        if 'y' not in ans.lower():
            print '''
    Where is it then?
        '''
            httpd_location = raw_input('>>')
        while not os.path.isfile(httpd_location):
            print '''
    That location isn\'t valid.\n\
    Please enter a valid location. (A)bort
    '''
            httpd_location = raw_input('>>')
            if 'a' == httpd_location.lower():
                sys.exit()

        # Write the conf file.
        old_httpd_conf = ''
        try:
            with open(httpd_location, 'a+') as f:
                old_httpd_conf = f.read()
                if conf not in old_httpd_conf:
                    f.write(conf)
        except IOError:
            print '''
    {0}[Error]{1}

    It looks like you don't have permission to edit {2}.
    If you can, edit your permissions and try again.
    Nothing has been changed.

    If you do not have permission to do this, please contact your sysadmin.

    If the problem persists, try the manual installation option.

    {3}[Advanced users only]{4} If you're confident that you won't
    accidentally mess something up, you can sudo this script and
    it should work.
    '''.format(bcolors.FAIL, bcolors.ENDC, httpd_location, bcolors.WARNING, bcolors.ENDC)
            sys.exit()

        # Check the Apache install.
        from subprocess import call
        print '''
    =========================================
    {0}Apache Syntax Check{1}
    =========================================

    ...
        '''.format(bcolors.HEADER, bcolors.ENDC)
        res = call(['apachectl', '-t'])

        # Rollback if there's any problem.
        if res > 0:
            print '''
            {0}[Error]{1} Something went wrong installing Microblogger in Apache.

            Rolling back httpd.conf.

            Check your apache conf file, then try again.
            '''.format(bcolors.FAIL, bcolors.ENDC)
            with open(httpd_location, 'w') as f:
                f.write(old_httpd_conf)
            print_manual_conf(conf)
            sys.exit()
        print '''
    Apache file: {0}[OK]{1}

    Press any enter to continue.
    '''.format(bcolors.OKGREEN, bcolors.ENDC)
        raw_input('>>')

        # Make the wsgi and cp it to the root of the web server.
        with open('bin/microblogger.wsgi', 'r') as f1:
            contents = f1.read()
            contents = contents.replace('{{WSGI_FILE_LOCATION}}', location + 'microblogger.wsgi')
            with open('microblogger.wsgi', 'w') as f2:
                f2.write(contents)

        # Crawler Crontab Setup.
        print '''
    =========================================
    {0}Web Crawler Setup{1}
    =========================================
    Setting up the crawler. This allows you to read other people's
    feeds and see their responses to you.

    The crawler is run as a cron job under the user specified
    for Apache earlier.

    Press enter to continue.
    '''.format(bcolors.HEADER, bcolors.ENDC)
        raw_input('>>')

        cron = CronTab(user=user)

        # Create a job to run the crawler.
        job = cron.new(command='/usr/bin/python {0}'.format(location + 'crawler/crawler.py'),
                comment='Microblogger: Runs the crawler automatically.')
        job.minute.every(1)

        # Check it's validity.
        if not job.is_valid:
            print '''
    {0}[Error]{1} Cron job is not valid.

    Exiting
    '''.format(bcolors.FAIL, bcolors.ENDC)
            sys.exit()

        cron.write()

        # Setup complete
        print '''
    =================================
    {0}Setup complete{1}
    ==================================
    Thank you for installing Microblogger. Welcome to the wonderful world
    of open, tamper-free communication.

    If you have any questions about Microblogger, please contact me via...

    Email: {2}brian@biteofanapple.com{3}
    OR
    Microblogger: {2}@sonicrocketman{3}

    Please restart Apache to begin using Microblogger.
    '''.format(bcolors.HEADER, bcolors.ENDC, bcolors.OKBLUE, bcolors.ENDC)


def signal_handler(signal, frame):
    """ Graceful shutdown. """
    sys.exit(0)


def print_manual_conf(conf):
    """ Prints the instructions for manual Apache installs. """
    print '''
    Please copy the following to the end of your Apache conf file.
    at /etc/httpd/conf/httpd.conf

    Press enter to continue.
    '''
    ans = raw_input('>>')
    os.system('cls' if os.name == 'nt' else 'clear')
    print conf


def validate_user(username):
    """ Checks if a user exist. """
    try:
        pwd.getpwnam(username)
    except KeyError:
        return False
    return True


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
