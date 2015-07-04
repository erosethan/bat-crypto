#!/usr/bin/python

import math
import random

class RSA:

  key_size = 0
  pack_size = 0

  def __init__(self, ksize = 8):
    self.key_size = max(ksize, 8)
    self.pack_size = self.key_size >> 3

  def FastExponentiation(self, a, n, m):
    if n == 0: return 1
    exp = self.FastExponentiation(
          (a * a) % m, n >> 1, m)
    if not (n & 1): return exp
    return (exp * a) % m

  def MillerRabin(self, n):
    k, m, a = 0, n - 1, random.randint(1, n - 1)
    while not (m & 1): m, k = m >> 1, k + 1
    b = self.FastExponentiation(a, m, n)
    if b == 1: return True
    for i in xrange(k):
      if b == n - 1: return True
      b = (b * b) % n
    return False

  def IsProbablePrime(self, n, iterations):
    if n == 1 or not (n & 1): return False
    for i in xrange(iterations):
      if not self.MillerRabin(n):
        return False
    return True

  def ExtendedEuclidian(self, a, b, m):
    if b == 0: return (a, 1, 0)
    (gcd, x, y) = self.ExtendedEuclidian(b, a % b, m)
    return (gcd, y, (x + m - ((a / b) * y) % m) % m)

  def GenerateKeys(self, acc = 100):
    p, q = 0, 0
    for i in xrange(self.key_size):
      p = (p << 1) | random.randint(0, 1)
      q = (q << 1) | random.randint(0, 1)
    while not self.IsProbablePrime(p, acc): p += 1
    while not self.IsProbablePrime(q, acc): q += 1
    n, phi, e = p * q, (p - 1) * (q - 1), 0
    while self.ExtendedEuclidian(e, phi, 1)[0] > 1:
      e = random.randint(2, phi - 1)
    d = self.ExtendedEuclidian(e, phi, phi)[1]
    if d < e: e, d = d, e
    return (e, n, d)

  def Encrypt(self, m, e, n):
    encrypted = ''
    p = self.pack_size
    l = (p - len(m) % p) % p
    for i in xrange(l): m += ' '
    for i in xrange(len(m) / p):
      group = 0
      for j in xrange(p):
        mi = ord(m[i * p + j])
        group = (group << 8) | mi
      group = self.FastExponentiation(group, e, n)
      encrypted += str(group) + ' '
    return encrypted.strip()

  def Decrypt(self, c, d, n):
    decrypted = ''
    for ci in c.split():
      ci, grp, buffer = int(ci), 0, ''
      mi = self.FastExponentiation(ci, d, n)
      while grp < self.pack_size:
        buffer += chr(mi & 255)
        grp, mi = grp + 1, mi >> 8
      decrypted += buffer[::-1]
    return decrypted.strip()

if __name__ == '__main__':

  rsa = RSA(32)
  (e, n, d) = rsa.GenerateKeys()
  encrypt = rsa.Encrypt('test rsa', e, n)
  decrypt = rsa.Decrypt(encrypt, d, n)
  print '%s -> %s' % (encrypt, decrypt)

