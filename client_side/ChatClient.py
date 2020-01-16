import socket
import ssl
import json
import struct
from threading import  Lock
import threading
import atexit
class ChatClient(threading.Thread):
    

    def __init__(self,chatip,chatport,sv_name,mycert,svcert,mykey):
        super(ChatClient,self).__init__()
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=svcert)
        context.load_cert_chain(certfile=mycert, keyfile=mykey)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_lock= Lock()
        self.sock = context.wrap_socket(s, server_side=False,server_hostname=sv_name)
        self.sock.connect((chatip, chatport))
        self.active= True
        self.raw_messages = list()
        self.recv_lock = Lock()

    def send_msg(self, key,val):
        data = json.dumps({key:val})
        msg = struct.pack('>I', len(data)) + data.encode()
        self.send_lock.acquire()
        try:
            self.sock.sendall(msg)
        except:
            pass
        finally:
            self.send_lock.release()

    def recvall(self,sock, n):
        data = bytearray()
        while len(data) < n:
            try:
                packet = sock.recv(n - len(data))
            except:
                packet = None
            if not packet:
                return None
            data.extend(packet)
        try:
            data = json.loads(data)
        except:
            pass
        return data


    def recv_msg(self):
        self.recv_lock.acquire()
        raw_msglen = self.recvall(self.sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        self.pinged=True
        msg = self.recvall(self.sock, msglen)
        self.recv_lock.release()
        return msg


    def run(self):
        while(self.active):
            data = self.recv_msg()
            threading.Thread(target = self.interpret,args=(data,)).start()
    
    def shutdown(self):
        self.active = False
        self.sock.close()
        del self


    def send(self,peerID,message):
        data = {'to':peerID,'content':message}
        self.send_msg('send',data)

    def interpret(self,data):
        print(data,type(data)," <<<<<<<<<<<< interpreting")
        if not data:
            return 1
        if data.get('ping',False):
            self.send_msg('ping','CL')
        
        if data.get('recv',False):
            self.raw_messages.append({'recv':data['recv']})
        
        return 0
        
    


if __name__=="__main__":

    import os
    path = os.path.dirname(__file__)
    server_cert = os.path.join(path,'certificates/cacert.pem')
    client_cert = os.path.join(path,'certificates/signed_certpem.pem')
    client_key = os.path.join(path,'certificates/test_key.pem')

    chat = ChatClient('127.0.0.1',80,'Simple CA',client_cert,server_cert,client_key)
    chat.start()
    atexit.register(chat.shutdown)

