#!/usr/bin/python

import random

def FastExponentiation(a, n, m):
  if n == 0: return 1
  exp = FastExponentiation(
        (a * a) % m, n >> 1, m)
  if not (n & 1): return exp
  return (exp * a) % m

def MillerRabin(n):
  k, m, a = 0, n - 1, random.randint(1, n - 1)
  while not (m & 1): m, k = m >> 1, k + 1
  b = FastExponentiation(a, m, n)
  if b == 1: return True
  for i in xrange(k):
    if b == n - 1: return True
    b = (b * b) % n
  return False

def IsProbablePrime(n, iterations):
  if n == 1 or not (n & 1): return False
  for i in xrange(iterations):
    if not MillerRabin(n):
      return False
  return True

def ExtendedEuclidian(a, b, m):
  if b == 0: return (a, 1, 0)
  (gcd, x, y) = ExtendedEuclidian(b, a % b, m)
  return (gcd, y, (x + m - ((a / b) * y) % m) % m)

def RSAGenerateKeys(size):
  p, q = 0, 0
  for i in xrange(size):
    p |= (1 << i) * random.randint(0, 1)
    q |= (1 << i) * random.randint(0, 1)
  while not IsProbablePrime(p, 100): p += 1
  while not IsProbablePrime(q, 100): q += 1
  n, phi, e = p * q, (p - 1) * (q - 1), 0
  while ExtendedEuclidian(e, phi, 1)[0] > 1:
    e = random.randint(2, phi - 1)
  d = ExtendedEuclidian(e, phi, phi)[1]
  if d < e: e, d = d, e
  return (n, e, d)

a = int(raw_input())  
keys = RSAGenerateKeys(a)
print keys
m = int(raw_input())
c = FastExponentiation(m, keys[1], keys[0])
print c
print FastExponentiation(c, keys[2], keys[0])

