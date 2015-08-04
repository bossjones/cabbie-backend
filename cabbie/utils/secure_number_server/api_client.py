from message import MessageBuilder


class ConsoleClient(LineReceiver):
    def __init__(self):
        pass

    def lineReceived(self, line):

        
class ConsoleClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        return ConsoleClient()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason


reactor.connectTCP('localhost', 5006, ConsoleClientFactory())
reactor.run() 
