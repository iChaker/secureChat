
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
def regen_key(new_key_path):

        key = rsa.generate_private_key( public_exponent=45451,
                                    key_size=2048,
                                    backend=default_backend())
        key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
        )
        with open(new_key_path, "wb") as f:
            f.write(key_pem)