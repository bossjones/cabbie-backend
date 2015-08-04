
from twisted.python import log
import settings
from utils import _hex2byte

# Message
# -------

# Structure
# request: operation class=className,attribute1Name=attribute1Value[,...][,where];
# response: res=s,op=operation,class=className[,error=ErrorCause]

# Operations

class MessageBuilder(object):



    # body
    OP_LOGIN, OP_LOGOUT, OP_SET, OP_CREATE, OP_DELETE = 'login', 'logout', 'Set', 'Create', 'Delete'
    CL_USER, CL_PN_INFO = 'user', 'PN_INFO'

    def login(self, username, password):
        return self._message(self.OP_LOGIN, self.CL_USER, name=username, passwd=password)       

    def logout(self):
        return self._message(self.OP_LOGOUT, self.CL_USER)
    
    def set(self, pk, **attr):
        """ Set phone number to 0506 number."""    
        where = { 'pn': pk } 
     
        return self._message(self.OP_SET, self.CL_PN_INFO, where=where, **attr) 

    def create(self, **attr):
        """ Create 0506 number entry."""    

        return self._message(self.OP_CREATE, self.CL_PN_INFO, **attr) 

    def delete(self, pk):
        """ Delete 0506 number entry."""
        where = { 'pn': pk }

        return self._message(self.OP_DELETE, self.CL_PN_INFO, where=where)

    def ping(self):
        return self.login(settings.USERNAME, settings.PASSWORD)


    def _make_header(self, data):
        headers = []
        headers.append(_hex2byte(settings.HEADER_REQUEST)) 
        
        # body length 
#       data_length_in_hex = hex(len(data)+1)[2:]
#       headers.append(_hex2byte(data_length_in_hex))

        import struct
        headers.append(struct.pack("i", len(data)+1))

        header = ''.join(headers)

        return header



    # helper
    def _message(self, op, class_name, where=None, **attributes):

        # body
        message_list = []
        message_list.append('{op} class={class_name}'.format(op=op, class_name=class_name))
        
        if attributes:
            attr = ','.join(['{k}={v}'.format(k=k, v=v) for k,v in attributes.iteritems()]) 
            message_list.append(',')
            message_list.append(attr)

        if where:
            where_clause = ','.join(['{k}={v}'.format(k=k, v=v) for k,v in where.iteritems()])
            message_list.append(',where ')
            message_list.append(where_clause)

        message_list.append(';')
        message = ''.join(message_list)

        # prefix header
        message = self._make_header(message) + message

        return message
