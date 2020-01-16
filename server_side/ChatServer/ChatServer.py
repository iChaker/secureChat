

import ssl
import socket
import threading
import struct
from time import sleep
from ClientThread import ClientThread
import gc

class ChatServer():

    def pingcnx(self,timeout,serial,connection):

        print("pinging ",str(serial))
        if not connection.ping(timeout):
            connection.drop()
            print("connection {}:{} Terminated due to Timeout".format(connection.addr[0],connection.addr[1]))
            del self.connections[serial]
            gc.collect()
        else :
            print("connection {}:{} pinged".format(connection.addr[0],connection.addr[1]))
        
        return 0


    def start_pinger(self,pingfreq,timeout,verbose):

        while not self.pinger.is_set():
            
            if len(self.connections) > 0:
                for serial , connection in self.connections.items():
                    threading.Thread(target=self.pingcnx,args=(timeout,serial,connection)).start()
            
            self.pinger.wait(timeout=pingfreq)
        return 0
                    
    def setpinger(self,pingfreq=120,timeout=1,active=True,verbose=False):
        if not active:
            self.pinger.set()
            print("pinger inactive")
        else:
            print("pinger is active")
            self.pinger.set()
            self.pinger.clear()
            threading.Thread(target=self.start_pinger,args=(pingfreq,timeout,verbose)).start()
            


    def ListenThread(self):

        while self.active:
            try:
                print("Waiting for client")
                newsocket, fromaddr = self.bindsocket.accept()
                conn = self.context.wrap_socket(newsocket, server_side=True)
                client = ClientThread(self,conn,fromaddr)
                client.start()


            except Exception as e:
                print(e)
    def __init__(self,sv_host,sv_port,ca_cert,ca_key,freq=120,timeout=1):
                
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.load_cert_chain(certfile=ca_cert, keyfile=ca_key)
        self.context.load_verify_locations(cafile=ca_cert)
        self.bindsocket = socket.socket()
        self.bindsocket.bind((sv_host, sv_port))
        self.bindsocket.listen(100)
        
        self.connections = dict()
        self.active=True
        self.pinger=threading.Event()
        threading.Thread(target=self.ListenThread).start()








if __name__=="__main__":
    import os
    path = os.path.dirname(__file__)
    ca_key = os.path.join(path,"../CA/ca_key.pem")
    ca_cert = os.path.join(path,"../CA/ca_cert.pem")
    chat = ChatServer("127.0.0.1",80,ca_cert,ca_key)
    chat.setpinger(pingfreq=10,timeout=2,verbose=True)

    