#!/usr/bin/python

import sys
import socket
import random
import threading
from rsa import *
from sdes import *

def ReadLine(sock):
  line_buffer = ''
  while True:
    try:
      byte = sock.recv(1)
      if not byte: break
      if byte == '\0': break
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
          sdes_info = rsa.Decrypt(ReadLine(sock),
            keys[2], keys[1]).split()
          sdes_key = int(sdes_info[0])
          sdes_iv = int(sdes_info[1])

          sdes = SDES(sdes_key)
          print '\n%s: %s' % (addr[0],
            sdes.Decrypt(ReadLine(sock), sdes_iv))
      finally:
        sock.close()
    except: pass

def SendMessageTo(addr):
  addr = addr.split(':')
  ip, port = addr[0], 7879
  if len(addr) > 1:
    port = int(addr[1])
  msg = raw_input('msg: ')
  try:
    server.send('G%s\0' % ip)
    keys = ReadLine(server).split()
    if len(keys) == 0:
      return 'send: %s is not online' % ip
  except: return 'send: Cannot reach server'
  try:
    e, n = int(keys[0]), int(keys[1])
  except: return 'send: Internal error'
  try:
    dest_sock = socket.socket(
      socket.AF_INET, socket.SOCK_STREAM)
    dest_sock.connect((ip, port))
    verification = rsa.Encrypt(ip, e, n)
    dest_sock.send('%s\0' % verification)

    sdes_iv = random.randint(1, 255)
    sdes_key = random.randint(1, 1023)
    sdes_info = '%d %d' % (sdes_key, sdes_iv)
    sdes_info = rsa.Encrypt(sdes_info, e, n)
    dest_sock.send('%s\0' % sdes_info)

    sdes = SDES(sdes_key)
    msg = sdes.Encrypt(msg, sdes_iv)
    dest_sock.send('%s\0' % msg)
  except: return 'send: Failed to send'
  return None

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
    server.send('%d %d\0' % (keys[0], keys[1]))
  except:
    print 'Connection to server failed!'
    sys.exit(0) # Abort client.

  client_running = True
  thread = threading.Thread(
    target = Receiver,
    args = (ip, port))
  thread.start()

  print 'Batcrypto client started!'
  print 'Listening @ %s:%d' % (ip, port)
  try:
    while True:
      input = raw_input('cmd: ').split()
      if len(input) == 0: continue

      command = input[0]
      if command == 'send':
        if len(input) > 1:
          error = SendMessageTo(input[1])
          if error != None: print error
        else: print 'send: Missing address'

      elif command == 'regen-keys':
        keys = rsa.GenerateKeys()
        print 'regen-keys: Keys regenerated!'
        server.send('U%d %d\0' % (keys[0], keys[1]))

      elif command == 'clear':
        for i in xrange(100): print ''
      elif command == 'shutdown': break
      else: print command + ': Command not found'
  except: pass
  finally:
    print '\nShutting down, bye!'
    client_running = False
    server.close()

