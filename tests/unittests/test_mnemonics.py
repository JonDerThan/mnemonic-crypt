from unittest import TestCase

from bitarray import bitarray

from mnemonic_crypt.mnemonics import *

_data_with_cs = [(bytes.fromhex(b), bitarray(cs)) for b, cs in [
    ("", ""),
    ("ff" * 3, ""),
    ("ff" * 4, "1"),
    ("0a" * 4, "0"),
    ("0a" * 32, "10111001")
]]

_mnemonics = [(bitarray(bits), indices, padding) for bits, indices, padding in [
    ("", [], 0),
    ("0" *  8, [0], 3),
    ("0" * 16, [0, 0], 6),
    ("0" * 24, [0, 0, 0], 9),
    ("0" * 32, [0, 0, 1], 0),
    ("1" * 32, [2047, 2047, 2047], 0),
    (bytes.fromhex("895c3c3f4006113e"), [1098, 1807, 126, 1024, 776, 1275], 0),
]]

class TestMnemonicConverter(TestCase):
    converter: MnemonicConverter

    def setUp(self):
        self.converter = MnemonicConverter.from_bip39_file()

    def test_bip39_import(self):
        c = self.converter
        self.assertEqual(2048, len(c.words))
        self.assertEqual(11, c.bitcount)
        self.assertEqual("abandon", c.words[0])
        self.assertEqual("zoo", c.words[-1])

    def test_checksum_generation(self):
        for b, cs in _data_with_cs:
            with self.subTest(f"{len(b) * 8} -> {len(cs)}"):
                self.assertEqual(cs, MnemonicConverter.generate_checksum(b))

    def test_invalid_checksum_verification(self):
        params = _data_with_cs[2:]
        for b, cs in params:
            bits = bitarray(b) + (cs ^ bitarray("1" * len(cs))) # invert checksum
            with self.subTest(cs.to01()):
                self.assertRaises(InvalidChecksum, lambda: MnemonicConverter.verify_checksum(bits))

    def test_valid_checksum_verification(self):
        for b, cs in _data_with_cs:
            b = bitarray(b)
            with self.subTest(cs.to01()):
                self.assertTupleEqual((b, cs), MnemonicConverter.verify_checksum(b + cs))

    def test_to_mnemonic(self):
        for i, (bits, indices, padding) in enumerate(_mnemonics):
            with self.subTest(str(i)):
                res = self.converter.convert_bytes(bits.tobytes())
                self.assertEqual(padding, res.padding)
                self.assertListEqual(indices, res.word_indices)

    def test_from_mnemonic(self):
        for i, (bits, indices, padding) in enumerate(_mnemonics):
            with self.subTest(str(i)):
                mnemonic = " ".join([self.converter.words[i] for i in indices]) + (
                    f" p{padding}" if padding > 0 else "")
                res = self.converter.convert_mnemonic(mnemonic)
                self.assertEqual(padding, res.padding)
                self.assertListEqual(indices, res.word_indices)
                self.assertEqual(bits, res.data)

    def test_with_invalid_word(self):
        self.assertRaises(InvalidMnemonicWord, lambda: self.converter.convert_mnemonic("inva1id"))
