from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import jwt
import logging
import os
from typing import Any
from typing import Tuple

import hashlib

ALGORITHM = os.environ.get("JWT_ALGORITHM") or "RS256"

# contributors: [agrawasa-12.11.23, nrobinso-12.11.23]
def hash_string_sha3_256(input_bytes: bytes):
    sha3_256_hash = hashlib.sha3_256()
    sha3_256_hash.update(input_bytes)
    hashed_string = sha3_256_hash.hexdigest()
    return hashed_string

# TODO: use a faster algorithm or one with a smaller key, e.g. ed25519

# contributors: [nrobinso-7.11.23]
def rs256_keypair(key_size:int=2048,public_exponent:int=65537)->Tuple[bytes,bytes]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return (private_key_pem, public_key_pem)


# contributors: [nrobinso-7.11.23]
class JWT:
    def __init__(self,algorithm=ALGORITHM):
        self.algorithm = algorithm
        print("ALGORITHM", self.algorithm)
        self.logger = logging.getLogger()
        # Generate new RSA key pair
        self.private_key, self.public_key = rs256_keypair()
        self.public_key_pem = self.public_key.decode("utf-8")
        self.key_name = self.hash_of_public_key()

    def hash_of_public_key(self):
        if not self.public_key:
            raise Exception
        return hash_string_sha3_256(self.public_key)

    def init_jwt(self, key_size:int=2048):
        # Generate new RSA key pair
        self.private_key, self.public_key = rs256_keypair(key_size=key_size)
        self.key_name = self.hash_of_public_key()
        if self.algorithm == 'none':
            self.private_key=None
    

    def encode(self, payload: dict[Any,Any]):
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def decode(self, token: str):
        if self.public_key:
            tok = jwt.decode(token, options={"verify_signature": False}, algorithms=[self.algorithm])
            return tok
        else:
            raise ValueError("Public key not available. Call init_jwt with a public key.")
        
    def valid_token(self, token: str, pub_key: str) -> bool:
        try:
            decode_result = jwt.decode(token, pub_key.encode("utf-8"), options={"verify_signaturue": True}, algorithms=[self.algorithm])
            print("decode result:", decode_result)
            return True
        except jwt.InvalidTokenError:
            return False

if __name__ == "__main__":
    j = JWT(algorithm='none')
    j.init_jwt()
    print(j.hash_of_public_key(), j.public_key)
    for i in range(100):
        jwtt = j.encode({"hello": "world"})
        print(len(jwtt.split(".")))
        print(j.decode(jwtt))
