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

# The tool reads mnemonic from stdin and converts it between bip39 and noomnem, and prints the result.
# For inputs with 12, 18, 24 words conversion is bip39 -> noomnem.
# For inputs with 16, 26, 37 words conversion is noomnem -> bip39.


import sys
from typing import Union, List

import vocab
from noomnem import noomnem_encode, noomnem_decode
from bip39 import bip39_encode, bip39_decode


def bip39_to_noomnem(words: Union[List[str], str]) -> str:
    if isinstance(words, list):
        words = ' '.join(words)
    entropy = bip39_decode(words)
    outwords = noomnem_encode(entropy)
    return ' '.join(outwords)


def noomnem_to_bip39(words: Union[List[str], str]) -> str:
    if not isinstance(words, list):
        words = words.split(' ')
    entropy = noomnem_decode(words)
    outwords = bip39_encode(entropy)
    return outwords


def main():
    s = sys.stdin.read()
    s = s.strip()
    words = s.split(' ')
    for w in words:
        if w not in vocab.mnemonic:
            print(f'word {w} is not in vocabulary')
            sys.exit(1)
    if len(words) in (12, 18, 24):
        outwords = bip39_to_noomnem(words)
    elif len(words) in (16, 26, 37):
        outwords = noomnem_to_bip39(words)
    else:
        sys.exit(1)

    print(outwords)
    sys.exit(0)


if __name__ == '__main__':
    main()

