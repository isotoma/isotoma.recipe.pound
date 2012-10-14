import os
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

if os.fork() == 0:
    if os.fork() == 0:
        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', int(sys.argv[1])), SimpleHTTPRequestHandler)
        httpd.handle_request()

