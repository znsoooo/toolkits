# -*- coding: utf-8 -*-

# build 20210114

# v2021
# UDP发消息TCP传文件
# 输入目标IP
# 文件MD5码作为文件名前缀以防止文件重名覆盖
# 发送时显示传送文件摘要
# 文件不存在时视为发送消息


import os, sys
import time
import socket
import hashlib
from threading import Thread

tk = __import__('Tkinter' if sys.version_info[0] == 2 else 'tkinter')

HOST    = socket.gethostbyname(socket.gethostname())
PORT    = 5009
BUFSIZE = 1024


def Md5(data):
    return hashlib.md5(data).hexdigest()[:6].upper()+ '_'


def GetFileData(file):
    if os.path.exists(file):
        with open(file, 'rb') as f:
            return f.read()
    return b''


def TcpSendFile(file, addr): # <file> can be in dirs
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((addr, PORT))

    # send file name
    client.send(file.encode())
    client.recv(BUFSIZE)
    data = GetFileData(file)
    # send file size
    client.send(str(len(data)).encode())
    client.recv(BUFSIZE)
    # send file md5
    client.send(Md5(data).encode())
    client.recv(BUFSIZE)

    size = len(data)
    for n in range(0, size, BUFSIZE):
        client.send(data[n:n+BUFSIZE])

    client.close()

    return size, os.path.split(file)[1]


def TcpRecvFile():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.bind(('', PORT)) 
    server.listen(5)
    client, (addr, port) = server.accept()

    # recv file name
    file = client.recv(BUFSIZE).decode()
    client.send(file.encode())
    # recv file size
    size = size2 = int(client.recv(BUFSIZE))
    client.send(str(size).encode())
    # recv file md5
    md5 = client.recv(BUFSIZE).decode()
    client.send(md5.encode())

    file2 = md5 + os.path.split(file)[1]
    if size:
        with open(md5 + os.path.split(file)[1], 'wb') as f:
            while size:
                block = client.recv(BUFSIZE)
                f.write(block)
                size -= len(block)

    client.close()
    server.close()

    return size2, file2


def Log(msg):
    print(msg)
    if app:
        app.title(msg)


def Receiver(u):
    def th():
        while RUN:
            cmd, msg = u.Recv().split('::', 1)
            if cmd == 'SEND':
                u.Send('RECV::%s'%msg)
                Log('Hear: %s'%msg)
            elif cmd == 'RECV':
                if os.path.exists(msg):
                    Log('Sending: "%s"'%msg)
                    u.Send('ACK1::'+msg)
                else:
                    Log('Msg: %s'%msg)
            elif cmd == 'ACK1':
                u.Send('ACK2::'+msg)
                Log('Recving: "%s"'%msg)
                size, file = TcpRecvFile()
                Log('Recved: "%s" (%d)'%(file, size))
            elif cmd == 'ACK2':
                size, file = TcpSendFile(msg, u.addr)
                Log('Sended: "%s" (%d)'%(file, size))

            if app:
                app.s1.set(u.addr)
                app.s2.set(msg)

    Thread(target=th).start()


class Udp:
    def __init__(self):
        self.so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.so.bind(('', PORT))
        self.addr = 'localhost'

    def Recv(self):
        data, (self.addr, port) = self.so.recvfrom(BUFSIZE)
        return data.decode()

    def Send(self, data, addr=None): # default addr is reply
        if addr is None:
            addr = self.addr
        self.so.sendto(data.encode(), (addr, PORT))

    def Close(self):
        self.so.close()


class MyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.s1 = tk.StringVar()
        self.s1.set(HOST)
        self.s2 = tk.StringVar()
        self.s2.set('demo.zip')

        btn1 = tk.Button(self, text='Send', command=self.Send)
        btn2 = tk.Button(self, text='Recv', command=self.Recv)
        ent1 = tk.Entry(self, textvariable=self.s1, width=15)
        ent2 = tk.Entry(self, textvariable=self.s2, width=30)

        ent1.pack(fill='both', side='left')
        ent2.pack(fill='both', side='left', expand=True)
        btn1.pack(fill='both', side='left')
        btn2.pack(fill='both', side='left')

        self.title('Transfer v2021')
        self.Center()

    def Center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.winfo_reqwidth())/2
        y = (self.winfo_screenheight() - self.winfo_reqheight())/2
        self.geometry('+%d+%d'%(x, y))

    def Send(self):
        addr = self.s1.get()
        mesg = self.s2.get()
        if mesg == '':
            mesg = tk.filedialog.askopenfilename()
        u.Send(('SEND::%s'%mesg), addr)

    def Recv(self):
        addr = self.s1.get()
        mesg = self.s2.get()
        if mesg != '':
            u.Send(('RECV::%s'%mesg), addr)



if __name__ == '__main__':
    RUN = True
    u = Udp()
    Receiver(u) # start udp receiver in back-thread
    app = None  # when tk-lib could not used
    app = MyApp()
    app.mainloop()
    app = None  # window closed
    RUN = False
    u.Close()
