from cryptography import x509 
from argparse import ArgumentParser
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import numpy as np
from cryptography.hazmat.primitives.asymmetric import padding
from hashlib import sha3_512
from datetime import datetime, timedelta
import ipaddress


class Requestor():

    def __init__(self,keyfile=None):
        if keyfile:
            self.key = self.load_key(keyfile)
  
    def load_key(self,key_path):
        with open(key_path,'rb') as key_file:
            key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
        return key

    def load_certificate(self,stream):
        return x509.load_pem_x509_certificate(stream,default_backend())
        
    def save_certificate(self,certificate,cert_filepath):
        with open(cert_filepath,'wb') as f:
            f.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))
    
    def generate_request(self,name,key):
        builder = x509.CertificateSigningRequestBuilder()
        builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, name)]))
        builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        request = builder.sign(key, hashes.SHA256(), default_backend())
        cert_pem = request.public_bytes(encoding=serialization.Encoding.PEM)
        return cert_pem
    
    def encrypt(self,public_key,message):
        ciphertext = public_key.encrypt( message, 
            padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
        
        return np.frombuffer(ciphertext,dtype='int8').tolist()

    
    def decrypt(self,numberlist):
        ciphertext = np.array(numberlist,dtype='int8').tobytes()
        plaintext = self.key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
        )

        return plaintext




