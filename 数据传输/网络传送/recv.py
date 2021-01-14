from socket import *

file = 'transfer.py'

s = socket(AF_INET,SOCK_DGRAM)
s.bind(('',5000))
data, addr = s.recvfrom(65536)
s.close()
with open(file,'wb') as f: f.write(data)

