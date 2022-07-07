# Copyright (C) 2022 Anton Shevchenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import vocab
from typing import Iterator

from noomnem import combi, combi2, bigint

# there are 2 schemes to encode (and decode) entropy into words.
# i have named them after 3rd pick in a trivial case for 2 elements from a set of 5 integers.
# suppose we have 5 integers (1, 2, 3, 4, 5) and we need to pick 2 elements of this set.
# one option is to use 'conventional' scheme: 1,2; 1,3; 1,4; 1,5; 2,3; 2,4; 2,5; 3,4; 3,5; 4,5.
# 3rd pick for this scheme is 1,4 - hence the name: scheme14.
# there is another approach to iterate over all combinations, it is less obvious but is more optimal in both
# encoding and decoding as it requires fewer cpu cycles to work.
# after picks 1,2 and 1,3 we increase the first element and not the second, so 3rd pick is 2,3 so the name: scheme23.
# the full set for scheme23 is the following: 1,2; 1,3; 2,3; 1,4; 2,4; 3,4; 1,5; 2,5; 3,5; 4,5.
# one may notice that scheme23 does not use numbers greater than necessary (subset of first 3 elements is full set for
# 3 elements; in the same way subset of first 6 elements if full set for 4 elements).
#
# for 3 elements out of same 5 the full set is: 1,2,3; 1,2,4; 1,3,4; 2,3,4; 1,2,5; 1,3,5; 2,3,5; 1,4,5; 2,4,5; 3,4,5.


# decodes given list of sorted ints into entropy value. scheme 14 is used.
# elems must be already sorted; maximum is other name for n.
def scheme14_decode_ints(elems: list[int], maximum: int = len(vocab.mnemonic)) -> bigint:
    count = len(elems)
    curmax = maximum
    result, base = 0, 0
    for idx, elem in enumerate(elems):
        cur = elem - base
        result += combi(curmax, count - idx) - combi(curmax - cur, count - idx)
        curmax -= cur + 1
        base = elem + 1
    return result


# encodes entropy (value parameter) into list of sorted ints.
# n defines number of elements in the set (as in combi); m defines number of elements in a pick.
def scheme14_encode_ints(value: bigint, n: int, m: int) -> list[int]:
    result = []
    base = 0
    curmax = n
    for left in range(m, 1, -1):
        cur = 1
        test = combi2(curmax, left) - combi2(curmax - cur, left)
        while test <= value:
            assert cur <= curmax - left
            cur += 1
            test = combi2(curmax, left) - combi2(curmax - cur, left)

        result.append(cur + base - 1)
        value -= combi2(curmax, left) - combi2(curmax - cur + 1, left)
        base += cur
        curmax -= cur
    # for last element we don't need a search
    result.append(value + base)
    return result


# generates (yields) all possible options to pick m elements from a set of n elements.
def scheme14_iterate(n: int, m: int) -> Iterator[list[int]]:
    assert n >= m
    arr = [i for i in range(m)]
    yield arr

    while True:
        idx = len(arr) - 1
        limit = n
        while idx >= 0:
            nextval = arr[idx] + 1
            if nextval < limit:
                arr[idx] = nextval
                break
            idx -= 1
            limit -= 1

        if idx < 0:  # the end
            break
        nextval = arr[idx] + 1
        idx += 1
        while idx < len(arr):
            arr[idx] = nextval
            nextval += 1
            idx += 1
        assert nextval <= n

        yield arr
