#!/usr/bin/python

import sys
import socket
import threading
from rsa import *

class ContactServer:

  serv_sock = None

  def __init__(self, addr, port = 7878):
    self.serv_sock = socket.socket(
      socket.AF_INET, socket.SOCK_STREAM)
    print 'Server running at %s' % addr
    self.serv_sock.bind((addr, port))
    print 'Binding at port %d' % port

  def Connection(self, sock, addr):
    print 'Testing'

  def Run(self, max_conn = 10):
    try:
      print 'Starting service now!'
      self.serv_sock.listen(max_conn)
      while True:
        print 'Waiting for new connection...'
        (sock, addr) = self.serv_sock.accept()
        print 'Connection from %s' % addr[0]
        thread = threading.Thread(
          target = self.Connection,
          args = (sock, addr))
        thread.start()
    except:
      print '\nServer shutted down'
      self.serv_sock.close()

if __name__ == '__main__':

  address = '127.0.0.1'
  if len(sys.argv) > 1:
    address = sys.argv[1]

  if len(sys.argv) > 2:
    port = int(sys.argv[2])
    server = ContactServer(address, port)
  else: server = ContactServer(address)

  server.Run()

