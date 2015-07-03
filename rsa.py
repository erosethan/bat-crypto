#!/usr/bin/python

import random

class RSA:

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

  def GenerateKeys(self, size, acc = 100):
    p, q = 0, 0
    for i in xrange(size):
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
    return self.FastExponentiation(m, e, n)

  def Decrypt(self, c, d, n):
    return self.FastExponentiation(c, d, n)

