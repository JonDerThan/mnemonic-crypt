import argon2
from math import ceil
from os import urandom
from time import time as now

_TYPE_TO_NAME = {
    argon2.Type.ID: "argon2id",
    argon2.Type.I : "argon2i",
    argon2.Type.D : "argon2d",
}

class Argon2Kdf:
    def __init__(self):
        pass

    @staticmethod
    def rnd_salt(size: int = 16) -> bytes:
        return urandom(size)

    @staticmethod
    def timed_raw(secret: str, salt: bytes, parameters: argon2.Parameters) -> tuple[float, bytes]:
        before = now()
        res = Argon2Kdf.raw(secret, salt, parameters)
        after = now()
        elapsed = after - before
        return (elapsed, res)

    @staticmethod
    def raw(secret: str, salt: bytes, parameters: argon2.Parameters) -> bytes:
        p = parameters
        assert p.hash_len == 32
        res = argon2.low_level.hash_secret_raw(
            secret=secret.encode("utf-8"),
            salt=salt,
            time_cost=p.time_cost,
            memory_cost=p.memory_cost,
            parallelism=p.parallelism,
            hash_len=32,
            type=p.type,
            version=p.version,
        )

        assert len(res) * 8 == 256, "aes key length"
        return res
    
    @staticmethod
    def default_parameters() -> argon2.Parameters:
        return argon2.profiles.get_default_parameters()

    @staticmethod
    def parameters_to_str(parameters: argon2.Parameters) -> str:
        # $argon2id$v=<num$m=<num>,t=<num>,p=<num>
        p = parameters
        assert p.hash_len == 32

        type = _TYPE_TO_NAME[p.type]
        return f"${type}$v={p.version}$m={p.memory_cost},t={p.time_cost},p={p.parallelism}"

    @staticmethod
    def str_to_parameters(s: str) -> str:
        # The argon2 encoded hash is usually of the form
        # $argon2id$v=<num>$m=<num>,t=<num>,p=<num>$<bin>$<bin>
        # where the last two values are the salt/hash, encoded in base64. The salt/hash length is
        # implied by these values. Padding is omitted.
        #
        # We however omit these last two values to just represent the parameters. To avoid manually
        # parsing the parameter string, we just add some dummy values here.

        bits_per_char = 6 # one base64 char encodes 6 bits
        if len(s.split("$")) == 4:
            # 16 bytes = 128 bits
            # 128 bits need >= 128 / 6 = 21.33 chars
            s += "$" + "A" * ceil(16 * 8 / bits_per_char)
            s += "$" + "A" * ceil(32 * 8 / bits_per_char)

        p = argon2.extract_parameters(s)
        assert p.salt_len == 16
        assert p.hash_len == 32
        return p
