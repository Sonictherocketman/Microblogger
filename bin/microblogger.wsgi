#!/usr/bin/python
import sys
sys.path.insert(0,"{{WSGI_FILE_LOCATION}}")

from webserver import app as application
