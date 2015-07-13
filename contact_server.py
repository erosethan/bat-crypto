#!/usr/bin/python

import sys
import time
import socket
import threading

class ContactServer:

  serv_sock = None
  is_active = False
  directory = dict()

  def __init__(self, addr, port):
    self.serv_sock = socket.socket(
      socket.AF_INET, socket.SOCK_STREAM)
    print 'Server running at %s' % addr
    self.serv_sock.bind((addr, port))
    print 'Binding at port %d' % port

  def RecvPackage(self, sock):
    buffer = ''
    while True:
      try:
        size = sock.recv(1)
        if not size: break
        if size == '\0': break
        size = ord(size)
        bytes = sock.recv(size)
        buffer += bytes
      except: pass
    return buffer

  def SendPackage(self, pack, sock):
    buffer = ['\0']
    try:
      for byte in pack:
        size = ord(buffer[0]) + 1
        buffer[0] = chr(size)
        buffer.append(byte)
        if size == 255:
          sock.send(''.join(buffer))
          buffer = ['\0']
      if buffer[0] != '\0':
        sock.send(''.join(buffer))
      sock.send('\0')
    except: return False
    return True

  def Connection(self, sock, addr):
    ip = addr[0]
    sock.settimeout(1)
    print 'Getting %s\'s key' % ip
    pkey = self.RecvPackage(sock)
    self.directory[ip] = pkey
    print '%s is now online!' % ip

    while self.is_active:
      try:
        cmd = sock.recv(1)
        if not cmd: break
        if cmd == 'U':
          pkey = self.RecvPackage(sock)
          self.directory[ip] = pkey
          print '%s updated his key' % ip
        elif cmd == 'G':
          query = self.RecvPackage(sock)
          pkey = self.directory.get(query, '')
          self.SendPackage(pkey, sock)
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
      print '\nShutting down, bye!'
      self.is_active = False
      self.serv_sock.close()

if __name__ == '__main__':

  address, port = '127.0.0.1', 7878

  if len(sys.argv) > 1:
    local = sys.argv[1]
    local = local.split(':')
    address = local[0]
    if len(local) > 1:
      port = int(local[1])

  server = ContactServer(
    address, port)
  server.Run()

