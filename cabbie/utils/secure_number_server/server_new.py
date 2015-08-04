from twisted.internet.protocol import Factory
from twisted.internet.base import DelayedCall
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, task
from twisted.python import log

from message import MessageBuilder
from crypto import encrypt, decrypt
import settings

class SecureNumber(LineReceiver):
    """
        Secure number server to communicate with SK Broadband G/W

        READY----->TRYLOGIN----->LOGIN----->TRYSET----->SET
                       \                       \
                        \------->LOGINFAIL      \------>SETFAIL
    """


    TEST = True

    HOST_SKBGW = '180.64.233.242' if not TEST else '127.0.0.1'
    
    PING_INTERVAL = 50

    # state constants
    STATE_READY, STATE_TRYLOGIN, STATE_LOGIN, STATE_LOGINFAIL, STATE_TRYSET, STATE_SET, STATE_SETFAIL = 'READY', 'TRYLOGIN', 'LOGIN', 'LOGINFAIL', 'TRYSET', 'SET', 'SETFAIL'

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = self.STATE_READY 
        self.message_builder = MessageBuilder()
        
        self.loopingCall = task.LoopingCall(self._ping)
        
        kw={'pn': '1234', 'default_in':'5678'}
        self.deferredCall = task.deferLater(reactor, 3, self.set, **kw)

    def _ping(self):
        message = self.message_builder.ping()

        self.transit(self.STATE_TRYLOGIN)
        self.sendLine(encrypt(message))
    
    def connectionMade(self):
        client_host, client_port = self.transport.client

        if client_host not in (self.HOST_SKBGW,):
            self.transport.loseConnection()

        self.name = client_host
        self.users[client_host] = self

        if client_host == self.HOST_SKBGW:
            self.transit(self.STATE_TRYLOGIN)
            message = self.message_builder.login(settings.USERNAME, settings.PASSWORD)

            # encrypt
            self.sendLine(encrypt(message))
            
            # start ping
            self.loopingCall.start(self.PING_INTERVAL, False)

    def connectionLost(self, reason):
        print 'Connection lost with reason {0}'.format(reason)

        if self.users.has_key(self.name):
            del self.users[self.name]

    @property
    def client_host(self):
        return self.transport.client[0]

    def skbgw_protocol(self):
        return self.users.get(self.HOST_SKBGW)

    def lineReceived(self, line):
        print 'Received {0} bytes'.format(len(line))

        if self.client_host == self.HOST_SKBGW: 
            # decrypt
            data = decrypt(line)

            header, body = data[:24], data[24:]

            # TODO: check header

            # parse body
            if self.state == self.STATE_TRYLOGIN:
                self.handle_LOGIN(body)
            elif self.state == self.STATE_TRYSET:
                self.handle_SET(body)

        else:
            if self.skbgw_protocol:
                key, op, pn, to, default_in = line.split()
                self.skbgw_protocol.set(pn, default_in)

    def set(self, pn, default_in):
        message = self.message_builder.set(pn, default_in=default_in)
        self.sendLine(encrypt(message))

    def handle_LOGIN(self, response):
        response = self._parse_response(response)        

        success = response.get('res') == 's' and response.get('op') == 'login' and response.get('class') == 'user' 

        if success:
            self.transit(self.STATE_LOGIN)
        else:
            self.transit(self.STAET_LOGINFAIL)
    
    def handle_SET(self, response):
        response = self._parse_response(response)        

        success = response.get('res') == 's' and response.get('op') == 'Set' and response.get('class') == 'PN_INFO' 

        if success:
            self.transit(self.STATE_SET)
        else:
            self.transit(self.STATE_SETFAIL)

    def _parse_response(self, data): 
        return dict([kv.split('=') for kv in data.split(';')[0].split(',')])
    
    def transit(self, state):
        print 'Transit from {old} to {new}'.format(old=self.state, new=state) 
        self.state = state 

class SecureNumberFactory(Factory):

    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return SecureNumber(self.users)

if __name__ == '__main__':
    reactor.listenTCP(5006, SecureNumberFactory())
    reactor.run()
