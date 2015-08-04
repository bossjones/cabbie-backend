from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

from sys import stdout

from message import MessageBuilder
from crypto import encrypt, decrypt
import settings

class SKBClient(LineReceiver):
    def __init__(self):
        self.message_builder = MessageBuilder()

    def lineReceived(self, line):
#        data = line.strip()
        data = line
        print 'Received {0} bytes'.format(len(data))

        self.respond(data)

    def respond(self, data):
        data = decrypt(data)

        header, body = data[:24], data[24:]

        print 'BODY  : {0}'.format(body)
        
        # login
        if body.split()[0] == 'login':        
            self.respond_to_LOGIN(body)

        # set
        elif body.split()[0] == 'Set': 
            self.respond_to_SET(body)

        else:
            print 'Not allowed statement {0}'.format(body)

    def parse_LOGIN(self, data):
        if len(data.split()) != 2:
            return None

        op, statement = data.split()
        
        if op != 'login':
            return None

        return self.parse_response(statement)

    def respond_to_LOGIN(self, data):
        statement = self.parse_LOGIN(data)

        body = None

        if statement.get('class') == 'user' and statement.get('name') == settings.USERNAME and statement.get('passwd') == settings.PASSWORD:
            body = 'res=s,op=login,class=user,pri=x,sec=x;'

        else:
            body = 'res=e,op=login,class=user,error=error'

        header = self.message_builder._make_header(body)

        print '{0}, {1}'.format(len(header), len(body))

        res = encrypt(header + body)
        print 'response size {0}'.format(len(res))

        self.sendLine(encrypt(header+body)) 

    def respond_to_SET(self, data):
        # TODO: to be implemented
        pass
         
    def parse_response(self, data):
        if not isinstance(data, basestring):
            return None            
        
        return dict([kv.split('=') for kv in data.split(';')[0].split(',')])




class SKBClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        return SKBClient()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason


reactor.connectTCP('localhost', 5006, SKBClientFactory())
reactor.run() 
