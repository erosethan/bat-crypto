#!/usr/bin/python

import sys
import time
import socket
import threading

class ContactServer:

  serv_sock = None
  is_active = False
  directory = dict()

  def __init__(self, addr, port = 7878):
    self.serv_sock = socket.socket(
      socket.AF_INET, socket.SOCK_STREAM)
    print 'Server running at %s' % addr
    self.serv_sock.bind((addr, port))
    print 'Binding at port %d' % port

  def ReadLine(self, sock):
    line_buffer = ''
    while True:
      try:
        byte = sock.recv(1)
        if not byte: break
        if byte == '\n': break
        line_buffer += byte
      except: pass
    return line_buffer

  def Connection(self, sock, addr):
    ip = addr[0]
    sock.settimeout(1)
    print 'Getting %s\'s key' % ip
    pkey = self.ReadLine(sock)
    self.directory[ip] = pkey + '\n'
    print '%s is now online!' % ip

    while self.is_active:
      try:
        cmd = sock.recv(1)
        if not cmd: break
        if cmd == 'U':
          pkey = self.ReadLine(sock)
          self.directory[ip] = pkey + '\n'
          print '%s updated his key' % ip
        elif cmd == 'G':
          query = self.ReadLine(sock)
          sock.send(self.directory.get(query, '\n'))
          print '%s got %s\'s key' % (ip, query)
      except: pass

    print '%s is now offline!' % ip
    del self.directory[ip]
    sock.close()

  def Run(self, max_conn = 10):
    try:
      self.is_active = True
      print 'Starting service now!'
      self.serv_sock.listen(max_conn)
      while True:
        print 'Waiting for new connection...'
        (sock, addr) = self.serv_sock.accept()
        thread = threading.Thread(
          target = self.Connection,
          args = (sock, addr))
        thread.start()
        time.sleep(0.1)
    except:
      print '\nServer shutted down'
      self.is_active = False
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

