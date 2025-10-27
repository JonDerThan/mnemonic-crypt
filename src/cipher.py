from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class DecryptionError(Exception):
    pass

class InvalidKeyError(DecryptionError):
    pass

class AesCipher:
    pad: PKCS7
    cipher: Cipher

    def __init__(self, key: bytes, iv: bytes):
        self.pad = PKCS7(128)
        aes = algorithms.AES256(key)
        cbc = modes.CBC(iv)
        self.cipher = Cipher(aes, cbc)

    def encrypt(self, data: bytes) -> bytes:
        padder = self.pad.padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()
        padder = None

        encr = self.cipher.encryptor()
        encrypted_data = encr.update(padded_data)
        encrypted_data += encr.finalize()
        encr = None

        return encrypted_data
    
    def decrypt(self, data: bytes) -> bytes:
        decr = self.cipher.decryptor()
        decrypted_data = decr.update(data)
        try:
            decrypted_data += decr.finalize()
        except ValueError:
            # probably invalid block length
            raise DecryptionError()
        decr = None

        unpadder = self.pad.unpadder()
        unpadded_data = unpadder.update(decrypted_data)
        try:
            # this fails when the padding doesn't make sense, which is the case when the key is wrong
            unpadded_data += unpadder.finalize()
        except ValueError:
            raise InvalidKeyError()
        unpadder = None

        return unpadded_data
