from socket import *
import time
import struct
myHost = '192.168.0.102'
myPort = 20001

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((myHost, myPort))

f = open("output/boss.bsi",'rb')

data = f.read()
f.close()

try:
    sockobj.send(data)
    sockobj.send("EOF")
    print "sending data"
except:
    print "socket error"

sockobj.close()