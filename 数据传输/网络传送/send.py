from socket import *

file = 'transfer.py'
addr = '127.0.0.1'
addr = '192.168.1.110'

with open(file,'rb') as f: data = f.read()
s = socket(AF_INET,SOCK_DGRAM)
s.sendto(data,(addr,5000))
s.close()
