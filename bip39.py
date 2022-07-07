import hashlib
from typing import List

import vocab


class AppError(Exception):
    def __init__(self, message: str):
        super().__init__(f"ERROR: {message} \nExiting.\n")


class EncodingError(AppError):
    """Raised if a given sequences of bytes cannot be encoded as BIP39 mnemonic phrase."""


class DecodingError(AppError):
    """Raised if a given BIP39 mnemonic phrase cannot be decoded into a sequence of bytes."""


def get_entropy_bits(num_words: int) -> int:
    """Returns the number of entropy bits in a mnemonic phrase with the given number of words.
    Raises a `DecodingError` if the given number of words is invalid.
    """
    try:
        return {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[num_words]
    except KeyError:
        raise DecodingError(
            "Invalid number of words provided, "
            "BIP39 mnemonic phrases are only specified for 12, 15, 18, 21, or 24 words."
        )


def bip39_encode(entropy: bytes) -> str:
    """Converts a given sequence of bytes into a BIP39 mnemonic phrase. This implementation only covers the English
    BIP39 wordlist as other wordlist are often poorly supported by other software and hardware devices.
    """
    num_bits_entropy = len(entropy) * 8
    num_bits_checksum = num_bits_entropy // 32
    num_words = (num_bits_entropy + num_bits_checksum) // 11
    if num_bits_entropy not in {128, 160, 192, 224, 256}:
        raise EncodingError(
            "Invalid number of bytes provided, "
            "BIP39 mnemonic phrases are only specified for 128, 160, 192, 224, or 256 bits."
        )

    # Compute the checksum as the first bits of the sha256 hash of the data.
    # As the checksum has at most 8 bits, we can directly access the first byte of the hash.
    checksum = hashlib.sha256(entropy).digest()[0] >> (8 - num_bits_checksum)

    # Covert the entropy to a number of easier handling of the 11-bit parts and append the checksum.
    entropy_and_checksum = (
        int.from_bytes(entropy, byteorder="big") << num_bits_checksum
    ) | checksum

    # Convert each 11 bit chunk into a word.
    remaining_data = entropy_and_checksum
    words: List[str] = []
    for _ in range(num_words):
        words.append(vocab.mnemonic[remaining_data & 0b111_1111_1111])
        remaining_data >>= 11

    # As we started with the conversion progress with the rightmost bits of `entropy_and_checksum` the list of words
    # needs to be reversed before we can join and return the final mnemonic phrase.
    words.reverse()
    return " ".join(words)


def bip39_decode(phrase: str) -> bytes:
    """Converts a given BIP39 mnemonic phrase to a sequence of bytes. The (weak) integrated checksum is verified and a
    `DecodingError` is raised in case the mnemonic is invalid. This implementation only covers the English BIP39
    wordlist as other wordlist are often poorly supported by other software and hardware devices.
    """
    if not all(c in " abcdefghijklmnopqrstuvwxyz" for c in phrase):
        raise DecodingError(
            f"Invalid mnemonic phrase {repr(phrase)} provided, phrase contains an invalid character."
        )

    words = phrase.split()
    num_bits_entropy = get_entropy_bits(len(words))
    num_bits_checksum = num_bits_entropy // 32

    bits = 0
    for word in words:
        bits <<= 11
        try:
            bits |= vocab.mnemonic_dict[word]
        except KeyError:
            raise DecodingError(
                f"Invalid mnemonic phrase {repr(phrase)} provided, word '{word}' is not in the BIP39 wordlist."
            )

    checksum = bits & (2 ** num_bits_checksum - 1)
    bits >>= num_bits_checksum
    data = bits.to_bytes(num_bits_entropy // 8, byteorder="big")

    checksum_for_verification = hashlib.sha256(data).digest()[0] >> (
        8 - num_bits_checksum
    )
    if checksum != checksum_for_verification:
        raise DecodingError(
            f"Invalid mnemonic phrase {repr(phrase)} provided, checksum invalid!"
        )

    return data
