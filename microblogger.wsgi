#!/usr/bin/python
import sys
sys.path.insert(0,"/var/www/microblogger/microblogger.wsgi")

from webserver import app as application
