import socket
import ssl
import json
import struct
from Requestor import Requestor
from threading import  Lock
import numpy as np
import threading
import atexit
import base64
class ChatClient(threading.Thread):
    

    def __init__(self,chatip,chatport,sv_name,mycert,svcert,mykey,event):
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
        self.requestor= Requestor(mykey)
        self.start()
        self.event = event

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

    def send_to(self,partner_cert,message):
        with open(partner_cert,'rb') as r:
            cert = self.requestor.load_certificate(r.read())
        content = self.requestor.encrypt(cert.public_key(),message.encode())
        to = '%x' % cert.serial_number

        send = {'to':to.upper(),'content':content}
        self.send_msg('send',send)
        


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
        if not data:
            return 1
        if data.get('ping',False):
            self.send_msg('ping','CL')
        
        if data.get('recv',False):

            content = self.requestor.decrypt(data['recv']['content'])
            self.event.set()
            self.raw_messages.append((data['recv']['from'],content))
        
        return 0
        
    


if __name__=="__main__":

    import os
    path = os.path.dirname(__file__)
    server_cert = os.path.join(path,'certificates/cacert.pem')
    client1_cert = os.path.join(path,'certificates/client1_cert.pem')
    client1_key = os.path.join(path,'certificates/test_key.pem')

    client2_cert = os.path.join(path,'certificates/client2_cert.pem')
    client2_key = os.path.join(path,'certificates/client2key.pem')

    #chat1 = ChatClient('127.0.0.1',80,'Simple CA',client1_cert,server_cert,client1_key)

    #chat2 = ChatClient('127.0.0.1',80,'Simple CA',client2_cert,server_cert,client2_key)

    #chat1.send_to("client_side/certificates/client2_cert.pem","hello")

    #initialization
    #chat = ChatClient()

    #send message
    #TODO  
    #chat.send_to(client2_cert.pem,"heelo")

    #handle event
    # what happens when this shit recieves a message

