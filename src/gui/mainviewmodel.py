from tkinter import StringVar, BooleanVar

from .validationvars import StringValidationVar, DataValidationError
from src.cipher import AesCipher, InvalidKeyError, DecryptionError
from src.mnemonics import MnemonicConverter, MnemonicConversionError
from src.key_derivation import Argon2Kdf

class MainViewModel:
    mnemonic_conv: MnemonicConverter

    plain_data_hex: StringValidationVar
    plain_data_mnemonic: StringValidationVar
    kdf_params: StringVar
    salt_hex: StringValidationVar
    salt_mnemonic: StringValidationVar
    password: StringVar
    encrypted_hex: StringValidationVar
    encrypted_mnemonic: StringValidationVar
    is_key_valid: BooleanVar

    _ignore_events: set
    _ignore_crypt_update: bool

    _cipher: AesCipher | None

    def __init__(self, mnemonic_converter: MnemonicConverter):
        self.mnemonic_conv = mnemonic_converter
        self._ignore_events = set()
        self._ignore_crypt_update = False

        kdf_params = Argon2Kdf.parameters_to_str(Argon2Kdf.default_parameters())

        self.plain_data_hex = StringValidationVar(self._on_hex_changed, name="plain_data_hex")
        self.plain_data_mnemonic = StringValidationVar(self._on_mnemonic_changed, name="plain_data_mnemonic")
        self.kdf_params = StringVar(value=kdf_params)
        self.salt_hex = StringValidationVar(self._on_hex_changed, name="salt_hex")
        self.salt_mnemonic = StringValidationVar(self._on_mnemonic_changed, name="salt_mnemonic")
        self.password = StringVar()
        self.encrypted_hex = StringValidationVar(self._on_hex_changed, name="encrypted_hex")
        self.encrypted_mnemonic = StringValidationVar(self._on_mnemonic_changed, name="encrypted_mnemonic")
        self.is_key_valid = BooleanVar(value=False)

        # invalidate cipher on
        # kdf params
        # salt hex
        # password
        self.salt_hex.trace_add("write", self._invalidate_key)
        self.kdf_params.trace_add("write", self._invalidate_key)
        self.password.trace_add("write", self._invalidate_key)

        self.encrypted_hex.write_cb.append(self._on_encrypted_hex_changed)
        self.plain_data_hex.write_cb.append(self._on_plain_data_hex_changed)

    def _invalidate_key(self, *_) -> None:
        self.is_key_valid.set(False)
        self._cipher = None

    def encrypt(self) -> None:
        if not self.plain_data_hex.valid:
            raise ValueError("invalid input data")

        data = bytes.fromhex(self.plain_data_hex.get())
        if len(data) == 0: return
        self.update_key()

        encrypted_data = self._cipher.encrypt(data)

        self._ignore_crypt_update = True
        self.encrypted_hex.set(encrypted_data.hex())
        self._ignore_crypt_update = False

    def decrypt(self) -> None:
        if not self.encrypted_hex.valid:
            raise ValueError("invalid encrypted data")

        encrypted_data = bytes.fromhex(self.encrypted_hex.get())
        if len(encrypted_data) == 0: return
        self.update_key()

        try:
            decrypted_data = self._cipher.decrypt(encrypted_data)
            self.encrypted_mnemonic.error_msg.set("")
            self.encrypted_mnemonic.valid = True
        except InvalidKeyError:
            self.encrypted_mnemonic.error_msg.set("Invalid decryption key.")
            self.encrypted_mnemonic.valid = False
            return
        except DecryptionError:
            self.encrypted_mnemonic.error_msg.set("Invalid ciphertext.")
            self.encrypted_mnemonic.valid = False
            return

        self._ignore_crypt_update = True
        self.plain_data_hex.set(decrypted_data.hex())
        self._ignore_crypt_update = False

    def update_key(self) -> None:
        if self.is_key_valid.get(): return
        params = self.kdf_params.get()
        params = Argon2Kdf.str_to_parameters(params)
        password = self.password.get()
        salt = bytes.fromhex(self.salt_hex.get())
        if len(salt) == 0:
            self.randomize_salt()
            salt = bytes.fromhex(self.salt_hex.get())

        (elapsed, key) = Argon2Kdf.timed_raw(password, salt, params)
        print(f"Calculated a new key in {round(elapsed, 4)}s.")

        self._cipher = AesCipher(key, salt)
        self.is_key_valid.set(True)

        plain_data = bytes.fromhex(self.plain_data_hex.get())
        if len(plain_data) > 0:
            self.encrypt()
        else:
            self.decrypt()

    def randomize_salt(self) -> None:
        new_salt = Argon2Kdf.rnd_salt()
        self.salt_hex.set(new_salt.hex())

    def _on_hex_changed(self, var_name: str, idx: str, mode: str) -> None:
        var_name_prefix = var_name.replace("_hex", "").replace("_mnemonic", "")
        if var_name_prefix in self._ignore_events: return
        hex_var = getattr(self, var_name_prefix + "_hex")
        mnemonic_var = getattr(self, var_name_prefix + "_mnemonic")
        new_val = hex_var.get()

        try:
            parsed_bytes = bytes.fromhex(new_val)
        except ValueError as e:
            raise DataValidationError("invalid hex string") from e

        res = self.mnemonic_conv.convert_bytes(parsed_bytes)
        mnemonic = res.str(omit_zero_padding=True)

        self._ignore_events.add(var_name_prefix)
        mnemonic_var.set(mnemonic)
        self._ignore_events.remove(var_name_prefix)

    def _on_mnemonic_changed(self, var_name: str, idx: str, mode: str) -> None:
        var_name_prefix = var_name.replace("_hex", "").replace("_mnemonic", "")
        if var_name_prefix in self._ignore_events: return
        hex_var = getattr(self, var_name_prefix + "_hex")
        mnemonic_var = getattr(self, var_name_prefix + "_mnemonic")
        new_val = mnemonic_var.get()

        try:
            res = self.mnemonic_conv.convert_mnemonic(new_val)
        except MnemonicConversionError as e:
            DataValidationError.raise_from_parent(e)

        data_hex = res.data.tobytes().hex()

        self._ignore_events.add(var_name_prefix)
        hex_var.set(data_hex)
        self._ignore_events.remove(var_name_prefix)

    def _on_encrypted_hex_changed(self, var_name: str, idx: str, mode: str) -> None:
        if self._ignore_crypt_update: return
        if not self.is_key_valid.get() or not self.encrypted_hex.valid: return

        self._ignore_crypt_update = True
        self.decrypt()
        self._ignore_crypt_update = False

    def _on_plain_data_hex_changed(self, var_name: str, idx: str, mode: str) -> None:
        if self._ignore_crypt_update: return
        if not self.is_key_valid.get() or not self.plain_data_hex.valid: return

        self._ignore_crypt_update = True
        self.encrypt()
        self._ignore_crypt_update = False
