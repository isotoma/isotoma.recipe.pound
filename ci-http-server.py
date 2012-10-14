import os
import sys
import signal
import time
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

if os.fork() == 0:
    child2 = os.fork()

    if child2 == 0:
        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', int(sys.argv[1])), SimpleHTTPRequestHandler)
        try:
            httpd.handle_request()
        except KeyboardInterrupt:
            pass

    if os.fork() == 0:
        time.sleep(10)
        os.kill(child2, signal.SIGINT)
    
