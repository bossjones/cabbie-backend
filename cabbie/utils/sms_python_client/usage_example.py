from http_client import HttpClient

httpmethod = "GET";
url = "http://api.openapi.io/ppurio/"
parameters = "?parameter=parameterValue&";
clientKey = "CLIENT_KEY";
contentType = "application/x-www-form-urlencoded";

# Create HttpClient
client = HttpClient()
     
# Http Method
response = client.sendRequest(httpmethod, url, parameters, clientKey, contentType)

# now you can do something with the response.
print vars(response)
