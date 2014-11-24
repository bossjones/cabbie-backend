import json
import urllib2

class RadixResponse:
    
    def __init__(self, response):
        self.raw_body = response.read()
        self.headers = response.info()
        self.code = response.getcode()
        self.body = self.raw_body
