#!/usr/bin/python

class SDES:

  k1, k2 = 0, 0

  S0 = [[1, 0, 3, 2],
        [3, 2, 1, 0], 
        [0, 2, 1, 3],
        [3, 1, 3, 2]]

  S1 = [[0, 1, 2, 3],
        [2, 0, 1, 3],
        [3, 0, 1, 0],
        [2, 1, 0, 3]]

  IP = [1, 5, 2, 0, 3, 7, 4, 6]
  FP = [3, 0, 2, 4, 6, 1, 7, 5]
  EP = [3, 0, 1, 2, 1, 2, 3, 0]

  P4  = [1, 3, 2, 0]
  P8  = [5, 2, 6, 3, 7, 4, 9, 8]
  P10 = [2, 4, 1, 6, 3, 9, 0, 8, 7, 5]

  def __init__(self, k):
    k = self.PermuteBits(k, self.P10, 10)
    self.k1, self.k2 = self.Shift(k, 1), self.Shift(k, 3)
    self.k1 = self.PermuteBits(self.k1, self.P8, 10)
    self.k2 = self.PermuteBits(self.k2, self.P8, 10)

  def PermuteBits(self, a, perm, bits):
    result = 0
    for i in perm:
      i = bits - i - 1
      result = result << 1
      if a & (1 << i):
        result = result | 1
    return result

  def CircularLeftShift(self, a, s, bits):
    exceed = 1 << bits
    for i in xrange(s):
      a = a << 1
      if a & exceed:
        a = a ^ exceed ^ 1
    return a

  def Shift(self, a, s):
    left, right = (a >> 5) & 31, a & 31
    left = self.CircularLeftShift(left, s, 5)
    right = self.CircularLeftShift(right, s, 5)
    return (left << 5) | right

  def Switch(self, a):
    return (a >> 4) & 15 | (a & 15) << 4

  def FunctionFk(self, a, k):
    left, right = (a >> 4) & 15, a & 15
    fk = self.PermuteBits(right, self.EP, 4) ^ k

    a = ((fk >> 7) & 1) << 1 | (fk >> 4) & 1
    b = ((fk >> 6) & 1) << 1 | (fk >> 5) & 1
    d = ((fk >> 2) & 1) << 1 | (fk >> 1) & 1
    c = ((fk >> 3) & 1) << 1 | fk & 1

    fk = self.S0[a][b] << 2 | self.S1[c][d]
    fk = self.PermuteBits(fk, self.P4, 4)
    return (left ^ fk) << 4 |  right

  def Encrypt(self, m, iv = 0):
    encrypted, previous = '', iv
    for char in m:
      char = ord(char) ^ previous
      char = self.PermuteBits(char, self.IP, 8)
      char = self.FunctionFk(char, self.k1)
      char = self.Switch(char)
      char = self.FunctionFk(char, self.k2)
      char = self.PermuteBits(char, self.FP, 8)
      encrypted += chr(char)
      previous = char
    return encrypted

  def Decrypt(self, c, iv = 0):
    decrypted, previous = '', iv
    for char in c:
      char = ord(char)
      ciph = self.PermuteBits(char, self.IP, 8)
      ciph = self.FunctionFk(ciph, self.k2)
      ciph = self.Switch(ciph)
      ciph = self.FunctionFk(ciph, self.k1)
      ciph = self.PermuteBits(ciph, self.FP, 8)
      decrypted += chr(ciph ^ previous)
      previous = char
    return decrypted

if __name__ == '__main__':

  m = raw_input()
  k = int(raw_input(), 2)

  sdes = SDES(k)
  enc = sdes.Encrypt(m)
  dec = sdes.Decrypt(enc)
  print '%s -> %s' % (enc, dec)

