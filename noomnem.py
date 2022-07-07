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

"""Reference implementation of Noo-Mnemonic (no-order mnemonic) entropy encoding."""


import vocab
import hashlib  # sha256, used only for checksum


# in python all ints are the same. when porting to other language it's better to know whether int means usual 32-bit
# integer (hinted as int in this module) or bigint data expected (bigint must hold up to 1024 bits).
bigint = int


# returns number of possible combinations to pick m elements from the set of n.
# for example, from the set of 5 elements {1, 2, 3, 4, 5} there are 5 options to pick 1 element (obviously);
# 10 options to pick 2 elements: [1, 2], [1, 3], [1, 4], [1, 5], [2, 3], [2, 4], [2, 5], [3, 4], [3, 5], [4, 5].
# mathematical notation for this kind of function is capital C with subscript n and superscript m.
# the formula is: C(n, m) = n! / ((n - m)! * m!) where x! is factorial of x.
# this is a pure function meaning result of the function is dependent only of arguments. this makes possible
# to precalc all data (and store it in a table) before first use (not implemented).
def combi(n: int, m: int) -> bigint:
    assert n > 0 and m >= 0
    assert m <= n <= 2048
    result = 1
    div = 1
    while div <= m:
        result = result * n // div
        n -= 1
        div += 1
    return result


# some inline tests
assert combi(5, 1) == 5
assert combi(5, 2) == 10
assert combi(10, 3) == 120


def combi2(n: int, m: int) -> bigint:
    if n < m:
        return 0
    return combi(n, m)


# returns truncated value of base 2 logarithm - meaning for values 5, 6 and 7 this function returns 2.
# logarithm answers the following question: to what exponent we need to raise base (in this case 2) to get the value.
# log2(4) == 2 as we need to use exponent 2 for the base 2 to obtain 4.
# log2(8) == 3 because 2 to the power of 3 equals 8.
def log2(n: bigint) -> int:
    result = 0
    while n >= 256:
        n >>= 8
        result += 8
    while n > 1:
        n //= 2
        result += 1
    return result


# some inline tests
assert log2(2048) == 11
assert log2(8) == 3
assert log2(7) == 2
assert log2(6) == 2
assert log2(5) == 2
assert log2(4) == 2


# returns upper bound value for logarithm of n with respect to base 2.
# upper bound means that for values between 4 and 8 we get the answer 3, hence upper bound.
def log2upper(n: int):
    result = 0
    while n > 1:
        n += 1
        n //= 2
        result += 1
    return result


assert log2upper(2048) == 11
assert log2upper(8) == 3
assert log2upper(7) == 3
assert log2upper(6) == 3
assert log2upper(5) == 3
assert log2upper(4) == 2


# encodes entropy (value parameter) into list of sorted ints. m defines number of elements in a pick.
# we don't need to know n for this scheme. what is scheme23? see a comment in scheme14.py
def scheme23_encode_ints(value: bigint, m: int) -> list[int]:
    result = []
    for i in range(m, 0, -1):
        cur = i
        test = combi2(cur, i)
        while test <= value:
            cur += 1
            test = combi2(cur, i)

        cur -= 1
        result.append(cur)
        value -= combi2(cur, i)
    return result[::-1]


# decodes given list of sorted ints into entropy value. scheme 23 is used. elems must be already sorted.
# why named scheme23? see a comment in scheme14.py
def scheme23_decode_ints(elems: list[int]) -> bigint:
    count = len(elems)
    result = 0
    while count > 0:
        result += combi2(elems[count-1], count)
        count -= 1
    return result


# returns number of words (from the standard 2048 words vocabulary) enough to derive given number of bits of entropy.
def calc_nwords(desired_entropy: int):
    for i in range(1, 1024):
        entropy = log2(combi(2048, i))
        if entropy >= desired_entropy:
            return i
    return None


assert calc_nwords(128) == 16  # 16 words enough to encode 131 bits of entropy
assert calc_nwords(192) == 26  # 26 words enough to encode 197 bits of entropy
assert calc_nwords(256) == 36  # 36 words enough to encode 257 bits of entropy

SUPPORTED_LENGTHS = {16: 128, 26: 192, 37: 256}  # key is number of words, value is bits of entropy encoded.
# for 256 bits we use 37 words. 36 words is enough to encode 257 bits but that means checksum is a single bit.
# 37th word adds extra 6 bits. so checksums are of size 3, 5, 7 bits for entropy length 128, 192, 256 bits respectively.
CHECKSUM_LENGTHS = {16: 3, 26: 5, 37: 7}

# reverse dictionary is used when we need to find key by knowing value.
# in this dictionary key is bits of entropy, and value is number of words.
SUPPORTED_LENGTHS_REVERSED = {v: k for k, v in SUPPORTED_LENGTHS.items()}


def _calc_checksum(data_without_checksum: bigint, len_words: int) -> int:
    data_len = SUPPORTED_LENGTHS[len_words] // 8
    data_bytes = data_without_checksum.to_bytes(data_len, 'big')
    hash = hashlib.sha256(data_bytes).digest()
    hashint = int.from_bytes(hash, 'big')
    mask = (1 << CHECKSUM_LENGTHS[len_words]) - 1
    return hashint & mask


# splits data into two components: data_without_checksum and checksum.
# input - data with checksum; returns tuple of (data_without_checksum, checksum)
def _extract_checksum(data: bigint, len_words: int) -> (bigint, int):
    checksum_len = CHECKSUM_LENGTHS[len_words]
    mask = (1 << checksum_len) - 1
    data_without_checksum = data >> checksum_len
    return data_without_checksum, data & mask


def _combine_checksum(data_without_checksum: bigint, len_words: int) -> bigint:
    checksum = _calc_checksum(data_without_checksum, len_words)
    data = (data_without_checksum << CHECKSUM_LENGTHS[len_words]) | checksum
    return data


def noomnem_decode(words: list[str]) -> bytes:
    """Decodes given list of words into bigint data."""
    # check input parameters
    len_words = len(words)
    if len_words not in SUPPORTED_LENGTHS.keys():
        raise ValueError('unsupported number of words ' + str(len_words + 1))

    # check words are in vocabulary
    ints = sorted([vocab.mnemonic_dict[w] for w in words])
    # check for repetitions
    for i in range(len(ints)-1):
        if ints[i] == ints[i+1]:
            raise ValueError('duplicate word at pos ' + str(i+1))

    # decode from array of ints into one bigint
    result = scheme23_decode_ints(ints)
    if log2(result) >= SUPPORTED_LENGTHS[len_words] + CHECKSUM_LENGTHS[len_words]:
        raise ValueError('decoded value is exceeding the limit')

    # extract, calculate and compare checksum
    result_without_checksum, checksum = _extract_checksum(result, len_words)
    calculated = _calc_checksum(result_without_checksum, len_words)
    if checksum != calculated:
        raise ValueError('checksum validation failed')
    return result_without_checksum.to_bytes(SUPPORTED_LENGTHS[len_words] // 8, 'big')


def noomnem_encode(data: bytes) -> list[str]:
    """Encodes given bigint data into list of words."""
    len_words = SUPPORTED_LENGTHS_REVERSED[len(data) * 8]
    if len_words not in SUPPORTED_LENGTHS.keys():
        raise ValueError('unsupported number of words ' + str(len_words + 1))
    intdata = int.from_bytes(data, 'big')
    assert log2(intdata) < SUPPORTED_LENGTHS[len_words]
    data_with_checksum = _combine_checksum(intdata, len_words)
    assert log2(data_with_checksum) < SUPPORTED_LENGTHS[len_words] + CHECKSUM_LENGTHS[len_words]
    ints = scheme23_encode_ints(data_with_checksum, len_words)
    return [vocab.mnemonic[i] for i in ints]
