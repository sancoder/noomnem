import unittest
from typing import Iterator
from noomnem import scheme23_decode_ints, scheme23_encode_ints


def scheme23_iterate(n: int, m: int) -> Iterator[list[int]]:
    assert n >= m
    cur = [i for i in range(m)]
    yield cur

    while True:
        idx = 0
        while idx < len(cur) - 1:
            if cur[idx] + 1 >= cur[idx + 1]:
                cur[idx] = idx
                idx += 1
            else:
                cur[idx] += 1
                yield cur
                # restart search for the next pick
                idx = 0

        # finished all options for current limit; limit = cur[len(cur)-1]; either increase limit or we're done.
        if cur[idx] + 1 < n:
            cur[idx] += 1
            yield cur
        else:
            break


class TestScheme23(unittest.TestCase):
    def do_test_n_m(self, n: int, m: int):
        count = 0
        for x in scheme23_iterate(n, m):
            self.assertEqual(count, scheme23_decode_ints(x))
            encoded = scheme23_encode_ints(count, m)
            self.assertEqual(encoded, x)
            count += 1

    def print_n_m(self, n: int, m: int):
        for x in scheme23_iterate(n, m):
            y = [i+1 for i in x]
            print(y, end=' ')
        print('')

    def test_10_3(self):
        self.do_test_n_m(10, 3)

    def test_25_4(self):
        self.do_test_n_m(25, 4)


if __name__ == '__main__':
    unittest.main()
