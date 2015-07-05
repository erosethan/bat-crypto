#!/usr/bin/python

import sys
import socket
import threading
from rsa import *

def ReadLine(sock):
  line_buffer = ''
  while True:
    try:
      byte = sock.recv(1)
      if not byte: break
      if byte == '\n': break
      line_buffer += byte
    except: pass
  return line_buffer

def Receiver(ip, port):
  recv_sock = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
  recv_sock.bind((ip, port))
  recv_sock.settimeout(1)
  recv_sock.listen(1)

  while client_running:
    try:
      (sock, addr) = recv_sock.accept()
      try:
        verification = rsa.Decrypt(
          ReadLine(sock), keys[2], keys[1])
        if verification == ip:
          sdes_onetime_key = rsa.Decrypt(
            ReadLine(sock), keys[2], keys[1])
          print sdes_onetime_key
      finally:
        sock.close()
    except: pass

def SendMessageTo(addr):
  print addr

if __name__ == '__main__':

  ip, port = '127.0.0.1', 7879
  sip, sport = '127.0.0.1', 7878

  if len(sys.argv) > 1:
    local = sys.argv[1]
    local = local.split(':')
    ip = local[0]
    if len(local) > 1:
      port = int(local[1])

  if len(sys.argv) > 2:
    serv = sys.argv[2]
    serv = serv.split(':')
    sip = serv[0]
    if len(serv) > 1:
      sport = int(serv[1])

  rsa = RSA(32)
  keys = rsa.GenerateKeys()
  try:
    server = socket.socket(
      socket.AF_INET, socket.SOCK_STREAM)
    server.connect((sip, sport))
    server.send('%d %d\n' % (keys[0], keys[1]))
  except:
    print 'Connection to server failed!'
    sys.exit(0) # Abort client.

  client_running = True
  thread = threading.Thread(
    target = Receiver,
    args = (ip, port))
  thread.start()

  try:
    while True:
      input = raw_input().split()
      if len(input) == 0: continue

      command = input[0]
      if command == 'send':
        if len(input) > 1:
          SendMessageTo(input[1])
        else: print 'send: Missing address'

      elif command == 'regen-key':
        keys = rsa.GenerateKeys()
        server.send('U%d %d\n' % (keys[0], keys[1]))

      elif command == 'shutdown': break
      else: print command + ': command not found'
  except: pass
  finally:
    print '\nShutting down, bye!'
    client_running = False
    server.close()

