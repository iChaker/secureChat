from cryptography import x509 
from argparse import ArgumentParser
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from hashlib import sha3_512
from datetime import datetime, timedelta
import ipaddress

#GENERATES CA KEY AND SELF SIGNED CERT
def renew_CA(issuer,certfile,keyfile):
    key = rsa.generate_private_key( public_exponent=45451,
                                    key_size=2048,
                                    backend=default_backend()
    )

    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, issuer)
    ])


    basic_contraints = x509.BasicConstraints(ca=True, path_length=0)
    now = datetime.utcnow()
    certbuilder= x509.CertificateBuilder()
    certbuilder= certbuilder.subject_name(name)
    certbuilder = certbuilder.issuer_name(name)
    certbuilder = certbuilder.public_key(key.public_key())
    certbuilder = certbuilder.serial_number(1)
    certbuilder = certbuilder.not_valid_before(now)
    certbuilder = certbuilder.not_valid_after(now + timedelta(days=10*365))
    certbuilder = certbuilder.add_extension(basic_contraints, False)
    certbuilder = certbuilder.sign(key, hashes.SHA256(), default_backend())
    

    cert_pem = certbuilder.public_bytes(encoding=serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with open(certfile, "wb") as f:
        f.write(cert_pem)

    with open(keyfile, "wb") as f:
        f.write(key_pem)
