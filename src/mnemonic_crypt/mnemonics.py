from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from hashlib import sha256
from dataclasses import dataclass
from importlib import resources as impresources
import math
import re

from mnemonic_crypt import wordlists

class MnemonicConversionError(ValueError):
    pass

class InvalidMnemonicWord(MnemonicConversionError):
    invalid_word: str

    def __init__(self, invalid_word: str):
        super().__init__(f"'{invalid_word}' is not a valid mnemonic word")
        self.invalid_word = invalid_word

class InvalidChecksum(MnemonicConversionError):
    expected: bitarray
    actual: bitarray

    def __init__(self, expected: bitarray, actual: bitarray):
        super().__init__("invalid checksum")
        self.expected = expected
        self.actual = actual

    @staticmethod
    def raise_if_invalid(expected: bitarray, actual: bitarray):
        if expected != actual:
            raise InvalidChecksum(expected, actual)

def format_mnemonic(mnemonic: str) -> str:
    words = mnemonic.split()

    decimal_digits = math.ceil(math.log(len(words), 10))
    largest_word = max(len(w) for w in words)

    numbered_words = [f"{str(i+1).rjust(decimal_digits)}. {w.ljust(largest_word)}" for (i, w) in enumerate(words)]

    column_count = 4
    rows = [numbered_words[i:min(i+column_count, len(words))] for i in range(0, len(words), column_count)]

    text = "\n".join("    ".join(row) for row in rows)
    return text

@dataclass
class MnemonicConversionResult:
    source: "MnemonicConverter"
    data: bitarray
    checksum: bitarray
    padding: int
    word_indices: list[int]

    def __str__(self) -> str:
        return self.str(omit_zero_padding=False)
    
    def str(self, omit_zero_padding: bool = False) -> str:
        words = [self.source.words[i] for i in self.word_indices]
        text = " ".join(words)
        if not omit_zero_padding or self.padding > 0:
            text += f" p{self.padding}"
        return text
    
    @staticmethod
    def empty(source: "MnemonicConverter") -> "MnemonicConversionResult":
        return MnemonicConversionResult(
            source=source,
            data=bitarray(),
            checksum=bitarray,
            padding=0,
            word_indices=[],
        )

class MnemonicConverter:
    word: list[str]
    bitcount: int

    def __init__(self, words: list[str]) -> None:
        self.words = words
        bitcount = math.log(len(self.words), 2)
        assert round(bitcount) - bitcount == 0, "has to be multiple of 2"
        self.bitcount = int(bitcount)
        assert self.bitcount == 11

    @staticmethod
    def from_bip39_file() -> "MnemonicConverter":
        words_file = impresources.files(wordlists) / "bip39-english.txt"
        with words_file.open("rt", encoding="utf8") as f:
            contents = f.read()

        words = contents.splitlines()
        return MnemonicConverter(words)

    @staticmethod
    def generate_checksum(data: bytes) -> bitarray:
        hash = bitarray(sha256(data).digest())
        cs_len = len(data) * 8 // 32
        return hash[:cs_len]

    @staticmethod
    def verify_checksum(bits: bitarray) -> tuple[bitarray, bitarray]:
        cs_len = len(bits) // 32
        cs_len = min(cs_len, 256)
        if cs_len == 0:
            return (bits, bitarray())
        data = bits[:-cs_len]
        expected_cs = bits[-cs_len:]
        hash = bitarray(sha256(data).digest())
        actual_cs = hash[:cs_len]
        InvalidChecksum.raise_if_invalid(expected_cs, actual_cs)
        return (data, actual_cs)

    def convert_bytes(self, data: bytes) -> MnemonicConversionResult:
        cs = self.generate_checksum(data)
        raw_bits = bitarray(data)
        bits = raw_bits + cs
        padding = (self.bitcount - (len(bits) % self.bitcount)) % self.bitcount
        bits = bits + bitarray("0" * padding)
        indices = []
        for i in range(0, len(bits), self.bitcount):
            slice = bits[i:i+self.bitcount]
            indices.append(ba2int(slice))

        return MnemonicConversionResult(
            source=self,
            data=raw_bits,
            checksum=cs,
            padding=padding,
            word_indices=indices,
        )

    def convert_mnemonic(self, text: str) -> MnemonicConversionResult:
        words = text.strip().split()

        if len(words) == 0:
            return MnemonicConversionResult.empty(self)

        padding = 0
        padding_match = re.match(r"^p([0-9]+)", words[-1])
        if padding_match is not None:
            padding = int(padding_match.group(1))
            del words[-1]

        indices = []
        for word in words:
            try:
                idx = self.words.index(word)
            except ValueError:
                raise InvalidMnemonicWord(word)
            indices.append(idx)

        bits = bitarray()
        for idx in indices:
            bits += int2ba(idx, length=11)

        if padding > 0:
            bits = bits[:-padding]

        (raw_bits, cs) = self.verify_checksum(bits)
        return MnemonicConversionResult(
            source=self,
            data=raw_bits,
            checksum=cs,
            padding=padding,
            word_indices=indices,
        )
