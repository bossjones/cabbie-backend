#!/usr/bin/env python

import socket

from cabbie.utils.secure_number_server import settings


if __name__ == '__main__':
    # socket creation
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(settings.TCP_ADDR)

    # connection

    
      
