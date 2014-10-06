import base64

from django.conf import settings
from Crypto.Cipher import AES


class Crypt(object):
    def __init__(self):
        self.aes = AES.new(settings.CRYPTO_KEY, AES.MODE_ECB)

    def encrypt(self, val):
        val = unicode(val).encode('utf-8')
        return base64.urlsafe_b64encode(self.aes.encrypt(val.ljust(
            ((len(val)-1) / 16 + 1) * 16
        )))

    def decrypt(self, val):
        return self.aes.decrypt(base64.urlsafe_b64decode(
            str(val))).decode('utf-8').strip()


def encrypt(val):
    return Crypt().encrypt(val)


def decrypt(val):
    return Crypt().decrypt(val)
