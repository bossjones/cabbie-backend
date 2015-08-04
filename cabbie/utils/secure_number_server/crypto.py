from utils import _hex2byte
import settings

from Crypto.Cipher import DES3
# DES3 Encryption : CBC mode
def encrypt(data):
    # right padding
    data = rpad(data)

    print 'Encrypt data {0}'.format(data)

    key = _hex2byte(settings.DES_CBC_ENCRYPTION_KEY)
    iv = _hex2byte(settings.DES_CBC_IV)
    des3 = DES3.new(key, DES3.MODE_CBC, iv)
    return des3.encrypt(data)

def decrypt(data):
    key = _hex2byte(settings.DES_CBC_ENCRYPTION_KEY)
    iv = _hex2byte(settings.DES_CBC_IV)
    des3 = DES3.new(key, DES3.MODE_CBC, iv)
    return des3.decrypt(data) 
 

def rpad(data):
    width = ( ( len(data) + 7 ) / 8 ) * 8
    data = data.ljust(width, '0')

    return data
