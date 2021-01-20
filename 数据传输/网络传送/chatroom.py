# -*- coding: utf-8 -*-

# Name:     Chatroom
# Version:  1.0.3
# Author:   Lishixian
# Website:  github.com/znsoooo/toolkits
# Python:   2.7/3.x
# Platform: Windows/Linux

# Useage:
# 上部消息记录,中间发送消息,左下角发送IP地址,可直接编辑,右键从列表中选择
# 窗口标题显示当前状态
# 当无法加载GUI库时依然可以满足运行
# 发送消息为文件夹路径时,返回本机或对方机文件列表
# 发送消息为文件路径时,发送或接收对应文件,文件名前缀增加文件MD5字符串
# 上线广播,获取所有在线的聊天室IP,下线广播,通知移出列表

# build 20210115

# TODO
# 当tkinter无法加载时
# 传文件进度条

# 窗口变化适配
# 快捷键
# 报错异常处理

import os, sys
import time
import socket
import hashlib
from threading import Thread

import traceback # for test

try:
    # raise # TODO for test no tk-module
    tk = __import__('Tkinter' if sys.version_info[0] == 2 else 'tkinter')
except:
    tk = False

LOG  = 'log.txt'

HOST    = socket.gethostbyname(socket.gethostname()) # TODO Linux获取地址是127.0.0.1
PORT    = 5009
BUFSIZE = 4096 # TODO 影响UDP消息最长字符(4096/3=1365)
CMD_LEN = 20   # MAX_LEN OF 'SEND::' AND SO ON


def Md5(data):
    return hashlib.md5(data).hexdigest()[:6].upper()+ '_'


def GetFileData(file):
    file2 = file.encode('u8') # Linux py27: unicode to str
    if os.path.isfile(file2):
        with open(file2, 'rb') as f:
            return f.read()
    return b''


def TcpSendFile(file, addr): # <file> can be with dirs
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((addr, PORT))

    # send file name
    client.send(file.encode('u8'))
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
    file = client.recv(BUFSIZE)
    client.send(file)
    # recv file size
    size = size2 = int(client.recv(BUFSIZE))
    client.send(str(size).encode())
    # recv file md5
    md5 = client.recv(BUFSIZE)
    client.send(md5)

    file2 = md5 + os.path.split(file)[1]
    if size:
        with open(file2, 'wb') as f:
            while size:
                block = client.recv(BUFSIZE)
                f.write(block)
                size -= len(block)

    client.close()
    server.close()

    return size2, file2.decode('u8')


def Title(msg):
    print([msg]) # Linux py27: print(str) always fail, but print(list) is good.
    if app:
        app.title(msg)


def LogFile(s=''):
    with open(LOG, 'ab+') as f:
        f.write(s.encode('u8'))
        f.seek(0)
        return f.read().decode('u8')


def Receiver(u):
    def th():
        while RUN:
            cmd, msg, addr = u.RecvCmd()
            # print((cmd, msg, addr)) # for test
            if app: # 前缀 SEND RECV BOOT ROBO ECHO AUTO FILE
                app.addrs.add(addr) # TODO 是否要排除自己?
                if cmd in ['SEND', 'RECV']:
                    app.Log('RECV', addr, msg)
                elif cmd == 'ECHO':
                    app.Log('ECHO', addr, msg)
                app.s3.set(addr)

            if cmd == 'SEND':
                u.SendCmd('REPL', msg)

            elif cmd in ['RECV', 'REPL']:
                result = []
                for s in msg.split('\n'):
                    s = s.encode('u8') # Linux py27: unicode to str
                    if os.path.isdir(s):
                        result += [os.path.join(s, file) for file in os.listdir(s)]
                    elif os.path.isfile(s):
                        s = s.decode('u8') # Linux py27: unicode to str
                        Title('Sending: "%s"'%s)
                        u.SendCmd('ACK1', s)
                if result:
                    ss = b'\n'.join(result) # use b'\n' for next line
                    ss = ss.decode('u8') # Linux py27: unicode to str
                    if cmd == 'RECV':
                        u.SendCmd('ECHO', ss)
                    elif app:
                        app.Log('ECHO', HOST, ss)

            elif cmd == 'ACK1':
                u.SendCmd('ACK2', msg)
                Title('Recving: "%s"'%msg)
                size, file = TcpRecvFile()
                Title('Recved: "%s" (%d)'%(file, size))
                if app:
                    app.Log('FILE', addr, 'Recv: %s'%file)

            elif cmd == 'ACK2':
                size, file = TcpSendFile(msg, addr)
                Title('Sended: "%s" (%d)'%(file, size))
                if app:
                    app.Log('FILE', HOST, 'Send: %s'%file)

            elif cmd == 'BROC':
                if msg == 'ONLINE':
                    u.SendCmd('BROC', 'REPEAT')
                elif msg == 'OFFLINE':
                    if app and addr in app.addrs:
                        app.addrs.remove(addr)

    Thread(target=th).start()


class Udp(socket.socket):
    def __init__(self):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(('', PORT))
        self.addr = 'localhost'

    def RecvCmd(self):
        data, (self.addr, port) = self.recvfrom(BUFSIZE)
        cmd, msg = data.decode('u8').split('::', 1)
        return cmd, msg, self.addr

    def SendCmd(self, cmd, msg, addr=None): # default addr is reply
        if addr is None:
            addr = self.addr
        self.sendto(('%s::%s'%(cmd, msg[:BUFSIZE-CMD_LEN])).encode('u8'), (addr, PORT))

    def Broadcast(self, msg):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.SendCmd('BROC', msg, '<broadcast>') # '<broadcast>', '255.255.255.255'
        self.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0) # TODO 必要的吗?


class MyMenu(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=0)

    def Update(self, options, command):
        self.delete(0, 'end')
        for label in options:
            self.AddCommand(label, command)

    def AddCommand(self, label, command):
        self.add_command(label=label, command=lambda: command(label))

    def Post(self, evt):
        self.post(evt.x_root, evt.y_root)


class MyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.addrs = {'localhost'}

        self.s3 = tk.StringVar()
        self.s3.set('localhost')

        btn1 = tk.Button (self, text='Send', command=lambda: self.Send('SEND'))
        btn2 = tk.Button (self, text='Recv', command=lambda: self.Send('RECV'))
        ent1 = tk.Entry  (self, width=12, textvariable=self.s3)
        self.s1 = tk.Text(self, width=60, height=24)
        self.s2 = tk.Text(self, width=60, height=8)
        self.ent1 = ent1

        self.s1.pack(fill='both', side='top', expand=True)
        self.s2.pack(fill='both', side='top')
        ent1.pack(fill='both', side='left', expand=True)
        btn1.pack(fill='both', side='left')
        btn2.pack(fill='both', side='left')

        try:
            ss = self.clipboard_get()
        except:
            ss = ''

        self.s1.insert(1.0, LogFile())
        self.s2.insert(1.0, ss)
        self.s1.see('end')
        self.s1.config(state='disabled')

        self.s2.focus()

        self.menu = MyMenu()
        ent1.bind('<ButtonRelease-3>', self.OnMenuPost)

        self.title('Chatroom (%s)'%HOST)
        self.Center()

    def OnMenuPost(self, evt):
        self.menu.Update(self.addrs, self.OnMenuSelect)
        self.menu.Post(evt)

    def OnMenuSelect(self, s):
        self.s3.set(s)
        self.ent1.icursor('end')

    def Center(self):
        self.withdraw() # withdraw/deiconify 阻止页面闪烁
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.winfo_reqwidth())/2
        y = (self.winfo_screenheight() - self.winfo_reqheight())/2
        self.geometry('+%d+%d'%(x, y))
        self.deiconify()

    def Log(self, typ, ip, msg):
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        s = '%s %s %s\n%s\n\n'%(typ, ip, t, msg)
        self.s1.config(state='normal')
        self.s1.insert('end', s)
        self.s1.config(state='disabled')
        self.s1.see('end')
        LogFile(s)

    def Send(self, cmd):
        addr = self.s3.get() # TODO addr=='<broadcast>'时发送广播消息
        msg  = self.s2.get(0.0, 'end')[:-1]
        u.SendCmd(cmd, msg, addr)
        self.Log('SEND', HOST, msg)


if __name__ == '__main__':
    RUN = True
    u = Udp()
    Receiver(u) # start udp receiver in back-thread
    app = None  # when tk-lib could not used
    app = MyApp()
    u.Broadcast('ONLINE')
    app.mainloop()

    app = None  # window closed
    RUN = False
    u.Broadcast('OFFLINE')
    u.close()
