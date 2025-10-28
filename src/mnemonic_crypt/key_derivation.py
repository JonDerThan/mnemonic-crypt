from dataclasses import dataclass
from enum import Enum
from math import ceil
from os import urandom
from time import time as now
import re

from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

class Argon2Type(Enum):
    ID = "argon2id"
    I  = "argon2i"
    D  = "argon2d"

@dataclass
class Argon2Parameters:
    type: Argon2Type
    version: int
    iterations: int # time cost
    memory_cost: int # KiB
    parallelism: int # no. of threads

    @staticmethod
    def default() -> "Argon2Parameters":
        """
        RFC9106 `FIRST RECOMMENDED` option with 2 iterations instead of 1.
        """
        assert 2**21 == 2_097_152 # 2 GiB
        return Argon2Parameters(
            type=Argon2Type.ID,
            version=19,
            iterations=2,
            memory_cost=2**21,
            parallelism=4,
        )

    @staticmethod
    def from_string(s: str) -> "Argon2Parameters":
        args = s.split("$")

        if len(args) != 4:
            raise ValueError("must include 4 $ signs to seperate parameters")
        
        if len(args[0]) > 0:
            raise ValueError("must start with a $ sign")
        
        argon_type_s = args[1]
        version_s = args[2]
        params = args[3].split(",")

        argon_type = None
        for t in Argon2Type:
            if argon_type_s == t.value:
                argon_type = t

        if argon_type is None:
            raise ValueError(f"unrecognized argon2 type: '{argon_type_s}'")
        
        if not version_s.startswith("v="):
            raise ValueError("invalid version string")
        
        version = int(version_s[2:])
        if version != 19:
            raise NotImplementedError(f"no support for version {version}")

        param_dict: dict[str, int] = {}
        for param in params:
            m = re.match(r"^([a-z])=([0-9]+)$", param)
            if m is None: raise ValueError("invalid param")
            key = m.group(1)
            value = int(m.group(2))
            if key in param_dict.keys(): raise ValueError(f"duplicate param {key}")
            param_dict[key] = value

        if len(param_dict) != 3: raise ValueError("invalid parameter count")
        invalid_keys = [key for key in param_dict.keys() if key not in ("m", "t", "p") ]
        if len(invalid_keys) > 0: raise ValueError(f"invalid key {key}")

        return Argon2Parameters(
            type=argon_type,
            version=version,
            memory_cost=param_dict["m"],
            iterations=param_dict["t"],
            parallelism=param_dict["p"],
        )

    def str(self) -> str:
        """
        PHC encoded parameters (without salt and key):
        `$argon2id$v=19$m=<memory_cost>,t=<iterations>,p=<lanes>`
        """
        p = self
        return f"${p.type.value}$v={p.version}$m={p.memory_cost},t={p.iterations},p={p.parallelism}"

class Argon2Kdf:
    def __init__(self):
        pass

    @staticmethod
    def rnd_salt(size: int = 16) -> bytes:
        return urandom(size)

    @staticmethod
    def timed_raw(secret: str, salt: bytes, parameters: Argon2Parameters) -> tuple[float, bytes]:
        before = now()
        res = Argon2Kdf.raw(secret, salt, parameters)
        after = now()
        elapsed = after - before
        return (elapsed, res)

    @staticmethod
    def raw(secret: str, salt: bytes, parameters: Argon2Parameters) -> bytes:
        p = parameters
        if p.type != Argon2Type.ID: raise NotImplementedError("can only calculate argon2id")
        if p.version != 19: raise NotImplementedError("can only calculate version 19")

        argon = Argon2id(
            salt=salt,
            length=32,
            iterations=p.iterations,
            lanes=p.parallelism,
            memory_cost=p.memory_cost,
        )

        res = argon.derive(secret.encode("utf-8"))
        assert len(res) * 8 == 256, "aes key length"
        return res
    
    @staticmethod
    def default_parameters() -> Argon2Parameters:
        return Argon2Parameters.default()

    @staticmethod
    def parameters_to_str(parameters: Argon2Parameters) -> str:
        return parameters.str()

    @staticmethod
    def str_to_parameters(s: str) -> Argon2Parameters:
        return Argon2Parameters.from_string(s)
