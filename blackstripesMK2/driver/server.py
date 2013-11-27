import asyncore, asynchat
import os, socket, string
import traceback
import warnings
import os
from subprocess import Popen

PORT = 20001

class Channel(asynchat.async_chat):

    def __init__(self, server, sock, addr, id):
        print "client connected ..."
        self.debug = 0
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator("EOF")
        self.request = None
        self.data = ""
        self.server = server
        self.error = 0
        
    def handle_close(self):
        print "client left ..."
        self.close()
        os._exit(0)
   
    def handle_error(self):
        self.error = 1
        asynchat.async_chat.handle_error(self)

    def push(self, data):
        if self.error:
            return
        asynchat.async_chat.push(self, data)

    def collect_incoming_data(self, data):
        self.data = self.data + data

    def found_terminator(self):
        if len(self.data) == 1000006:
            self.parseRequest()
        else:
             print "ERROR : image incomplete"    
        self.data = ""
        
    def parseRequest(self):
        try:
            f = open("image.bin",'wb')
            f.write(self.data)
            f.close()

            os.chdir(os.getcwd())

            if os.path.isfile("spiral.bin"):
                print "motiondata found ..."
            else:
                print "ERROR : motiondata not found"
                self.close()
                os._exit(-1)

            if os.path.isfile("image.bin"):
                print "image found ..."
            else:
                print "ERROR : image not found"
                self.close()
                os._exit(-1)

            Popen(["./driver", "spiral.bin","image.bin"],close_fds=True)

        except:
            print "RMI ERROR"
            traceback.print_exc(file=self)
            
    def write(self,msg):
        print msg

            
class Server(asyncore.dispatcher):

    def __init__(self, port):
        self.client_id = 0
        self.clients = {}
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("", port))
        self.listen(5)

    def handle_accept(self):
        self.client_id = self.client_id + 1
        conn, addr = self.accept()
        ch = Channel(self, conn, addr, self.client_id)
        self.clients[self.client_id] = ch
             
if __name__ == '__main__':
    warnings.filterwarnings('ignore','.*',DeprecationWarning)
    s = Server(PORT)
    print "serving at port", PORT, "..."
    asyncore.loop(2)
    

