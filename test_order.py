import random
import unittest
from noomnem import noomnem_decode, noomnem_encode


class TestOrdering(unittest.TestCase):

    def test_reverse_order(self):
        ba = bytearray(i for i in range(16))
        words = noomnem_encode(ba)
        print(words)
        words = words[::-1]
        print(words)
        test = noomnem_decode(words)
        self.assertEqual(bytes(ba), test)

    def test_minimum_entropy(self):
        ba = bytearray([0] * 16)
        words = noomnem_encode(ba)
        print('minimum', words)
        random.shuffle(words)
        test = noomnem_decode(words)
        self.assertEqual(bytes(ba), test)

    def test_maximum_entropy(self):
        ba = bytearray([255] * 16)
        words = noomnem_encode(ba)
        words = words[::-1]
        print('maximum', words)
        random.shuffle(words)
        test = noomnem_decode(words)
        self.assertEqual(bytes(ba), test)
