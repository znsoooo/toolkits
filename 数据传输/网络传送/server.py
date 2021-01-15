import os
import socket

HOST = '' 
PORT = 21567  
BUFSIZ = 1024  
ADDR = (HOST, PORT)

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpSerSock.bind(ADDR) 
tcpSerSock.listen(5)    

while True:
    try:
        print('waiting for connection...')
        tcpCliSock, addr = tcpSerSock.accept()
        print ('...connected from:', addr)
        while True:
            command = tcpCliSock.recv(BUFSIZ).decode()
            print('command:', command)
            tcpCliSock.send('command received'.encode())
            if command == 'SEND':
                file_name = tcpCliSock.recv(BUFSIZ).decode()
                tcpCliSock.send('file_name received'.encode())
                file_total_size = int(tcpCliSock.recv(BUFSIZ).decode())
                tcpCliSock.send('file_total_size received'.encode())
                received_size = 0
                f = open('new' + file_name  ,'wb')
                while received_size < file_total_size:
                    data = tcpCliSock.recv(BUFSIZ)
                    f.write(data)
                    received_size += len(data)
                f.close()
                print('total: %s, received: %s'%(file_total_size,received_size))
            elif command == 'RECV':
                file_name = tcpCliSock.recv(BUFSIZ).decode()
                print('recv:',file_name)
                if not file_name:
                    break
                if os.path.exists(file_name):
                    file_size = str(os.path.getsize(file_name))
                    tcpCliSock.send(file_size.encode())
                    back = tcpCliSock.recv(BUFSIZ).decode()
                    print('St send:',file_size)
                    f = open(file_name, 'rb')
                    for line in f:
                        tcpCliSock.send(line)
                    print('Fin send')
                else:
                    tcpCliSockck.send('0001'.encode())
        tcpCliSock.close()
    except Exception as e:
        print('Exception:', e) # when client not closed and restart
tcpSerSock.close()
