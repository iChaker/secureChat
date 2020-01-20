
from Requestor import Requestor
import socket
import ssl
import threading

class csr_client():     

    def __init__(self,ca_ip,ca_port,name,key_path,cert_path,cacert_path):
        

        requestor = Requestor()
        client_key = requestor.load_key(key_path)
        csr = requestor.generate_request(name,client_key)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ca_ip,ca_port))
        sock.send(csr)
        down_stream = sock.recv(1024)
        certificate = requestor.load_certificate(down_stream)
        requestor.save_certificate(certificate,cert_path)
        down_stream = sock.recv(1024)
        certificate = requestor.load_certificate(down_stream)
        requestor.save_certificate(certificate,cacert_path)


if __name__=="__main__":
    import os
    path = os.path.dirname(__file__)
    key = os.path.join(path,"./certificates/client2key.pem")
    cert = os.path.join(path,"./certificates/client2_cert.pem")
    cacert = os.path.join(path,"./certificates/cacert.pem")
    import threading
    threading.Thread(target=csr_client, args=("127.0.0.1",80,"me2",key,cert,cacert)).start()