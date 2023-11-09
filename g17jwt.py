from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import jwt
import logging

ALGORITHM="RS256"


# contributors: [nrobinso-7.11.23]
def rs256_keypair(key_size=2048,public_exponent=65537):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
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
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.logger = logging.getLogger()

    def init_jwt(self, key_size=2048):
        # Generate new RSA key pair
        self.private_key, self.public_key = rs256_keypair()

    def encode(self, payload):
        if self.private_key:
            return jwt.encode(payload, self.private_key, algorithm=ALGORITHM)
        else:
            raise ValueError("Private key not available. Call init_jwt with a private key.")

    def decode(self, token):
        if self.public_key:
            tok = jwt.decode(token, options={"verify_signature": False}, algorithms=[ALGORITHM])
            return tok
        else:
            raise ValueError("Public key not available. Call init_jwt with a public key.")
