from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
import gc
from datetime import datetime, timedelta
import functools
from cryptography import x509 
from uuid import uuid4

class Signer():

    def __init__(self,ca_cert_path, ca_key_path):
        self.private_key = None
        self.private_key_path = ca_key_path
        with open(ca_cert_path,"rb") as f:
            self.ca_cert= x509.load_pem_x509_certificate(f.read(),default_backend())
        self.load_private_key()

    def load_private_key(self):
        if os.path.isfile(self.private_key_path):
            with open(self.private_key_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
        else:
            print("Wrong Path")
    
    def unload_private_key(self):
        self.private_key = None
        gc.collect()

    def get_public_key(self):
        return self.ca_cert.public_key()

    def get_CA_cert(self):
        return self.ca_cert

    def download_csr(self,csrb):
        return x509.load_pem_x509_csr(csrb,default_backend())

    def sign(self,csr):
        now = datetime.utcnow()
        certbuilder= x509.CertificateBuilder()
        certbuilder= certbuilder.subject_name(csr.subject)
        certbuilder = certbuilder.issuer_name(self.ca_cert.issuer)
        certbuilder = certbuilder.public_key(csr.public_key())
        certbuilder = certbuilder.serial_number(int(uuid4()))
        certbuilder = certbuilder.not_valid_before(now- timedelta(days=1))
        certbuilder = certbuilder.not_valid_after(now + timedelta(days=10*365))
        for ext in csr.extensions:
            certbuilder = certbuilder.add_extension(ext.value,ext.critical)
        certificate = certbuilder.sign(self.private_key, hashes.SHA256(), default_backend())

        return certificate
    
    def upload_certificate(self,cert):
        return cert.public_bytes(encoding=serialization.Encoding.PEM)


    




            
