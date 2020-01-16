
from Signer import Signer
import socket
import ssl
import threading

def signThread(conn,signer,cacert,fromaddr):
    
    print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
    try:
        down_stream = conn.recv(1024)
        csr = signer.download_csr(down_stream)
        print("Connection {}:{} recieved valid certificate request".format(fromaddr[0], fromaddr[1]))
        certificate = signer.sign(csr)
        conn.send(signer.upload_certificate(certificate))
        print("Connection {}:{} signed and uploaded certificate".format(fromaddr[0], fromaddr[1]))
        conn.send(cacert)
        print("Connection {}:{} uploaded CA cert".format(fromaddr[0], fromaddr[1]))
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        print("Connection {}:{} terminated successfully".format(fromaddr[0], fromaddr[1]))
        return 0
        
    except Exception as e:
        print("Connection {}:{} ERROR: {}".format(fromaddr[0], fromaddr[1],e))
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        return 1

#this server signs every certificate request(CSR)
class caserver():

    def listenThread(self):
        
        while self.flag:
            print("Signer waiting for new connection")
            newsocket, fromaddr = self.server.accept()
            threading.Thread(target=signThread, args=(newsocket,self.signer,self.cert,fromaddr), name="connection listener").start()
        return 0            

    def __init__(self,host,port,cert,key):
        
        self.port = port
        self.host = host
        with open(cert,'rb') as cf:
            self.cert = cf.read()
        self.key = key
        self.signer = Signer(cert,key)
        self.flag = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users = {} 
        
        try:
            self.server.bind((self.host, self.port))
            print("SERVER SUCCESSFULLY BINDED")
        except socket.error:
            print('Bind failed %s' % (socket.error))
       
        self.server.listen(2)

    
    def startsigner(self):
        if not self.flag:
            self.flag = True
            threading.Thread(target=self.listenThread,name="Signer").start()
        
        print("Signer Is Active")
    def stopsigner(self):
        self.flag = False
        print("Signer Is inactive")


if __name__=="__main__":
    import os
    path = os.path.dirname(__file__)
    cert = os.path.join(path,"ca_cert.pem")
    key = os.path.join(path,"ca_key.pem")
    sv = caserver("127.0.0.1",80,cert,key)
    sv.startsigner()
    #sv.stopsigner
