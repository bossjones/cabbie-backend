#!/usr/bin/env python

import socket

from tornado.tcpserver import TCPServer

from Crypto.Cipher import DES

from message import MessageBuilder
import settings 

#                   |                               |   
#   1. API Server  <->  2. Secure Number Server    <->  3. SKB G/W
#                   |                               |

# Protocols btw. 1,2
# 1. set {pn} to {default_in};

# Protocols btw. 2,3
# 1. handshake
# 2. ping-pong
# 3. send set

# Examples
# 1. handshake and login
# 2. ping-pong
# 3. set operation


# DES3 Encryption : CBC mode
def encrypt(data):
    key = _hex2byte(settings.DES_CBC_ENCRYPTION_KEY)
    iv = _hex2byte(settings.DES_CBC_IV)
    des3 = DES.new(key, DES.MODE_CBC, iv)
    return des3.encrypt(data)

def decrypt(data):
    key = _hex2byte(settings.DES_CBC_ENCRYPTION_KEY)
    iv = _hex2byte(settings.DES_CBC_IV)
    des3 = DES.new(key, DES.MODE_CBC, iv)
    return des3.decrypt(data) 
    

# hexadecimal helper 
def _hex2byte( hexStr ):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case    
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )
 
    bytes = []

    hexStr = ''.join( hexStr.split(" ") )

    for i in range(0, len(hexStr), 2):
        bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

    return ''.join( bytes )



class SecureNumberTCPServer(TCPServer):
    # Origin
    OP_SET = 'set'

    def __init__(self, *args, **kwargs):
        super(SecureNumberTCPServer, self).__init__(*args, **kwargs)

        self._stream = None 

        self.message_builder = MessageBuilder()

    def _make_header(self, data):
        headers = []
        headers.append(_hex2byte(settings.HEADER_REQUEST)) 
        
        # body length 
        data_length_in_hex = hex(len(data)+1)[2:]
        headers.append(_hex2byte(data_length_in_hex))

        header = ''.join(headers)

        print header
        return header

    # ----------------------
    # interface with SKB G/W
    # ---------------------- 

    # 1. handshake (send login on connection)
    # 2. ping-pong (send login to ping)
    # 3. set (send set)


    def handle_stream(self, stream, address):
        """ handle new stream """

        print 'Connection from address={address}\tdata={data}'.format(address=address, data=stream)

        self._stream = stream

        login_message = self.message_builder.login(settings.USERNAME, settings.PASSWORD)
        self.send(login_message)

        stream.read_until_close(settings.BUFFER_SIZE, streaming_callback=on_data)

    def send(self, data, callback=None):
        """ prefix header, encrypt, and send """
        data = self._make_header(data) + data
        self._stream.write(encrypt(data)) 

    def on_data(self, data):
        """ callback on data reception """

        print '[SKB] Data received: {0}'.format(data)
         
        if isinstance(data, basestring):
            # header, body
            data = data.strip()

            # data => header, body
            header, body = data[:settings.HEADER_BYTE_LENGTH], data[settings.HEADER_BYTE_LENGTH:] 

            # 1. login success/error
            # - success : res=s,op=login,class=user,pri=x,sec=x;
            # - error   : res=e,op=login,class=user,error=(ErrorCause);
            # 2. set success/error
            # - success : res=s,op=Set,class=[classname];
            # - error   : res=e,op=Set,class=[classname],error=(ErrorCause);
            # 3. ping
            response = self.parse_response(body) 
            print '[SKB] Response {0}'.format(response)            
    
        else:
            print '[SKB] Received data is not basestring: {data}'.format(data=data)
            return
 
    def parse_response(self, data):
        data = decrypt(data)

        if not isinstance(data, basestring):
            return None            
        
        return dict([kv.split('=') for kv in data.split(';')[0].split(',')])



if __name__ == '__main__':
    sn_server = SecureNumberTCPServer()
    sn_server.bind(settings.TCP_PORT) 
    sn_server.start(0)
    IOLoop.current().start()
 
