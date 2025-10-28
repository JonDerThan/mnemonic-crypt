from argparse import ArgumentParser, Namespace
import sys
from typing import Any

from .cipher import AesCipher
from .key_derivation import Argon2Kdf
from .mnemonics import MnemonicConverter, MnemonicConversionError, format_mnemonic

class Cli:
    parser: ArgumentParser
    args: Namespace
    mnemonic_conv: MnemonicConverter

    def __init__(self):
        p = ArgumentParser(
            prog="MnemonicCrypt",
            description="Encrypts data/a mnemonic and outputs the used salt and ciphertext encoded "
            "as a mnemonic",
            epilog="Note: use single quotes ' for the arguments, otherwise the $ signs in strings "
            "get intepreted as variables by your shell."
        )
        p.add_argument("command", choices=("encrypt", "decrypt"))
        p.add_argument("--data", "-d", help="Can be a mnemonic or a hex string.")
        p.add_argument("--password", "-p")
        p.add_argument("--salt", "-s")
        p.add_argument("--kdf-params", "-k")
        p.add_argument("--no-pretty-print", "-u", action="store_true")

        self.parser = p

    def run(self) -> None:
        self.args = self.parser.parse_args()

        # TODO: make this configurable via cli argument
        self.mnemonic_conv = MnemonicConverter.from_bip39_file()

        data = self._get_bytes_from_arg(self.args.data, "data")
        pw = self._get_pw()

        cmd = self.args.command
        if cmd == "encrypt":
            self._encrypt(data, pw)
        elif cmd == "decrypt":
            self._decrypt(data, pw)
        else:
            raise NotImplementedError(f"'{cmd}' is not implemented")

    def _encrypt(self, data: bytes, pw: str) -> None:
        salt = self.args.salt
        if salt is not None:
            salt = self._get_bytes_from_arg(salt, "salt")
        else:
            salt = Argon2Kdf.rnd_salt()
    
        kdf_params = self.args.kdf_params
        if kdf_params is not None:
            kdf_params = Argon2Kdf.str_to_parameters(kdf_params)
        else:
            kdf_params = Argon2Kdf.default_parameters()

        cipher = self._create_cipher(pw, salt, kdf_params)
        encrypted_data = cipher.encrypt(data)

        encrypted_mnemonic = self._encode_to_mnemonic(encrypted_data)
        salt_mnemonic = self._encode_to_mnemonic(salt)
        kdf_params_str = Argon2Kdf.parameters_to_str(kdf_params)

        if self.args.no_pretty_print:
            print(f"{encrypted_mnemonic}\n{salt_mnemonic}\n{kdf_params_str}")
        else:
            print(f"Encrypted mnemonic:\n{format_mnemonic(encrypted_mnemonic)}")
            print(f"\nSalt:\n{format_mnemonic(salt_mnemonic)}")
            print(f"\nKDF:\n{kdf_params_str}")

    def _decrypt(self, data: bytes, pw: str) -> None:
        salt = self._ensure_arg(self.args.salt, "when decrypting data a salt must be specified")
        salt = self._get_bytes_from_arg(salt, "salt")

        kdf_params = self.args.kdf_params
        if kdf_params is not None:
            kdf_params = Argon2Kdf.str_to_parameters(kdf_params)
        else:
            print("No KDF parameters defined, using default ones...", file=sys.stderr)
            kdf_params = Argon2Kdf.default_parameters()

        cipher = self._create_cipher(pw, salt, kdf_params)

        # TODO: error handling
        decrypted_data = cipher.decrypt(data)

        decrypted_mnemonic = self._encode_to_mnemonic(decrypted_data)

        if self.args.no_pretty_print:
            print(decrypted_mnemonic)
        else:
            print(f"Decrypted mnemonic:\n{format_mnemonic(decrypted_mnemonic)}")

    def _encode_to_mnemonic(self, data: bytes) -> str:
        res = self.mnemonic_conv.convert_bytes(data)
        return res.str(True)

    def _get_pw(self) -> str:
        pw = self.args.password
        if pw is None:
            # TODO: read pw from stdin after command executes
            raise ValueError("you must specify a password")
    
        return pw

    def _get_bytes_from_arg(self, s: str, arg_name: str) -> bytes:
        try:
            return self._get_bytes_from_hex_or_mnemonic(s)
        except ValueError:
            self.parser.print_usage()
            print(f"error: could not extract data from --{arg_name}: must be either a mnemonic or "
                  "a hex string")
            sys.exit(1)

    def _get_bytes_from_hex_or_mnemonic(self, s: str) -> bytes:
        b = None
        try:
            res = self.mnemonic_conv.convert_mnemonic(s)
            b = res.data.tobytes()
        except MnemonicConversionError:
            try:
                b = bytes.fromhex(s)
            except ValueError:
                pass
            
        if b is None:
            raise ValueError("could not get data from the string")
        if len(b) == 0:
            raise ValueError("no data to parse")
        return b

    def _ensure_arg(self, arg: str, err_msg: str) -> str:
        if arg is not None: return arg
        self.parser.print_usage()
        print("error: " + err_msg, file=sys.stderr)
        sys.exit(1)

    def _create_cipher(self, pw: str, salt: bytes, kdf_params) -> AesCipher:
        (elapsed, key) = Argon2Kdf.timed_raw(pw, salt, kdf_params)
        print(f"Calculated key in {round(elapsed, 4)}s.", file=sys.stderr)
        cipher = AesCipher(key, salt)
        return cipher

def main():
    cli = Cli()
    cli.run()

if __name__ == "__main__":
    main()
