"""
Network connections
"""

try:
    # Python 3
    import http.client as httplib
except ImportError:
    import httplib

try:
    # Python 3
    import urllib.parse as urlparse
except ImportError:
    import urlparse

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
        pass
    

