import sys
import urllib
import urllib2
import base64

from multipart_post_handler import MultipartPostHandler
from radix_response import RadixResponse 

class HttpClient: 

    def sendRequest(self, httpmethod, url, parameters, clientKey, contentType):

        auth_value = clientKey
        headers = {}
        headers["x-waple-authorization"] = auth_value
        headers["Content-type"] = contentType

        data = None

        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')

        opener = urllib2.build_opener(MultipartPostHandler)
        
        if (httpmethod == "GET"):
            url = url + "?" + parameters
        else:
            data = urllib.urlencode(parameters)
        
        request = urllib2.Request(url, data, headers)
        request.get_method = lambda: httpmethod
        
        try:
            response = opener.open(request)
        except urllib2.HTTPError, e:
            if e.getcode() == 500:
                response = e
            else:
                import sys
                response = "Error executing the request "+ str(sys.exc_info()[1])

        return RadixResponse(response)
       



