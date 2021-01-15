# TODO repeat file names?

import os
import time
import socket
try:
    import tkinter
except:
    import Tkinter as tkinter

HOST = '192.168.1.120' # '192.168.1.176' # 'localhost'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

def Send(path):
    cnt = 0
    cnt_step = 5000

    if path == '':
        path = tkinter.filedialog.askopenfilename()
    file_name = path.split('/')[-1]
    ss.set(file_name)

    tcpCliSock.send('SEND'.encode())
    back = tcpCliSock.recv(BUFSIZ).decode()
    if os.path.exists(file_name):
        tcpCliSock.send(file_name.encode())
        back = tcpCliSock.recv(BUFSIZ).decode()
        file_size = str(os.path.getsize(file_name))
        tcpCliSock.send(file_size.encode())
        back = tcpCliSock.recv(BUFSIZ).decode()
        print('Start send:',file_size)
        f = open(file_name, 'rb')
        send_size = 0
        for line in f:
            send_size += len(line)
            tcpCliSock.send(line)
            cnt = cnt + 1
            if cnt > cnt_step:
                print('Sended: %s'%send_size)
                cnt = 0
        print('All: %s, Send: %s'%(file_size,send_size))
    else:
        tcpCliSock.send('0001'.encode())


def Recv(path):
    cnt = 0
    cnt_step = 5000
    if path != '':
        file_name = path.split('/')[-1]
        tcpCliSock.send('RECV'.encode())
        back = tcpCliSock.recv(BUFSIZ).decode()
        tcpCliSock.send(file_name.encode())
        file_size = tcpCliSock.recv(BUFSIZ).decode()
        tcpCliSock.send('file_size received'.encode())
        if file_size == '0001':
            print('File not found: %s'%file_name)
        else:
            print('St recv:',file_size)
            file_size = int(file_size)
            received_size = 0
            f = open('new' + file_name  ,'wb')
            while received_size < file_size:
                data = tcpCliSock.recv(BUFSIZ)
                f.write(data)
                received_size += len(data)
                cnt = cnt + 1
                if cnt > cnt_step:
                    print('Recved: %s'%received_size)
                    cnt = 0
            f.close()
            print('All: %s, Recv: %s'%(file_size,received_size))

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())/2
    y = (top.winfo_screenheight() - top.winfo_reqheight())/2
    top.geometry('+%d+%d'%(x,y))

tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpCliSock.connect(ADDR)

top = tkinter.Tk()

ss = tkinter.StringVar()
ss.set('demo.stl')

bt1 = tkinter.Button(top,text='Send',command=lambda:Send(ent.get()))
bt2 = tkinter.Button(top,text='Recv',command=lambda:Recv(ent.get()))
ent = tkinter.Entry(top,textvariable=ss)
ent.grid(row=0,column=0)
bt1.grid(row=0,column=1)
bt2.grid(row=0,column=2)
setCenter(top)
top.mainloop()

tcpCliSock.close()

