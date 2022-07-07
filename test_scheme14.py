import unittest

from scheme14 import scheme14_iterate, scheme14_decode_ints, scheme14_encode_ints


class TestScheme14(unittest.TestCase):
    def do_test_n_m(self, n: int, m: int):
        count = 0
        for x in scheme14_iterate(n, m):
            self.assertEqual(count, scheme14_decode_ints(x, maximum=n))
            encoded = scheme14_encode_ints(count, n, m)
            self.assertEqual(encoded, x)
            count += 1

    def print_n_m(self, n: int, m: int):
        for x in scheme14_iterate(n, m):
            y = [i+1 for i in x]
            print(y, end=' ')
        print('')

    def test_10_3(self):
        self.do_test_n_m(10, 3)

    def test_25_4(self):
        self.do_test_n_m(25, 4)


if __name__ == '__main__':
    unittest.main()
