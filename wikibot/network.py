"""
Network connections
"""

import sys

import util

if util.py_version == 2:
    import httplib
    import urlparse
elif util.py_version == 3:
    import http.client as httplib
    import urllib.parse as urlparse
else:
    util.die('Unsupported python version:', util.py_version)

class Request:
    def __init__(self, url, data={}, method="GET", auto=True, async=False, callback=None):
        purl = urlparse.urlparse(url)  # Parsed URL
        
        self.host, self.port, self.path, self.data, self.method = \
            purl.hostname, purl.port, purl.path, data, method
        
        self.async, self.callback = async, callback
        
        if auto:
            self.request()
    
    def request(self):
        self.conn = httplib.HTTPConnection(self.host, self.port)
        
    def fetch(self):
        self.conn.request(self.method, self.path)
        return self.conn.getresponse()
    

