# noomnem
Presented here is a new mnemonic encoding called NoO-Mnemonic (No Order Mnemonic). With this encoding user is no longer required to remember order of words in mnemonic, only the words itself. Hence the name “No Order Mnemonic”. Vocabulary used is the same as in BIP-39.

With BIP-39 it is necessary to know 12 words (and the order) to derive entropy of 128 bits length. Using NoO-Mnemonic it is necessary to know 16 words for the same length. Same way, for 192 bits, number of words increases from 18 to 26. For 256 bits, number of words increases from 24 to 37. Encoding does not use word repetitions, i.e. any word in the mnemonic could appear only once.

```
import noomnem
import random
bin = random.randbytes(16)  # 128 bits
words = noomnem.noomnem_encode(bin)
random.shuffle(words)
decoded = noomnem.noomnem_decode(words)
assert decoded == bin
```
