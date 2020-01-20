import struct
import json
from threading import Thread, Lock, Event

from time import sleep
import gc

class ClientThread(Thread):
    

    def __init__(self,server,conn,addr):
        super(ClientThread,self).__init__()
        self.addr = addr
        self.sock = conn
        self.send_lock = Lock()
        self.recv_lock = Lock()
        self.cert = conn.getpeercert()
        self.active = True
        self.server = server
        self.pinged = Event()
        self.server.connections[self.getcert()['serialNumber']] = self
        print("THREAD INITIALIZED {}:{}".format(addr[0],addr[1]))

    def run(self):
        print("THREAD RUNNING {}".format(self.getcert()['subject']))
        while(self.active):
            data = self.recv_msg()
            Thread(target=self.interpret,args=(data,)).start()

    def drop(self):
        self.active=False
        
    def ping(self,timeout):
        self.pinged.clear()
        self.send_msg('ping','SV')
        self.pinged.wait(timeout=timeout)

        return self.pinged.is_set()
            
    def recvall(self,sock, n):
        data = bytearray()
        while len(data) < n:
            try:
                packet = sock.recv(n - len(data))
                self.pinged.set()
            except:
                packet = False
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
        msg = self.recvall(self.sock, msglen)
        self.recv_lock.release()
        return msg


    def interpret(self,data):
        if not data:
            return 1
        if data.get('ping',False):
            pass
        if data.get('send',False):
            message = data['send']
            if self.server.connections.get(message['to'],False):
                if self.server.connections[message['to']].ping(2):
                    self.server.connections[message['to']].send_msg('recv',{'from': self.getcert()['serialNumber'],'content' :message['content']})
                else:
                    self.send_msg('error','recipient disconnected')
                    self.server.connections[message['to']].drop()
                    del self.server.connections[message['to']]
            else:
                self.send_msg('error','recipient disconnected')
                self.server.connections[message['to']].drop()
                del self.server.connections[message['to']]
                gc.collect()
        return 0
        


    def send_msg(self, key,val):
        data = json.dumps({key:val})
        msg = struct.pack('>I', len(data)) + data.encode()
        self.send_lock.acquire()
        try:
            self.sock.sendall(msg)
        except Exception:
            pass
        finally:
            self.send_lock.release()


    def getcert(self):
        return self.cert