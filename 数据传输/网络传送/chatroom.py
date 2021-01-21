# -*- coding: utf-8 -*-

# Name:     Chatroom
# Version:  1.0.5
# Author:   Lishixian
# Website:  github.com/znsoooo/toolkits
# Platform: Windows/Linux
# Python:   2.7/3.x

# Useage:
# 上部消息记录,中间发送消息,左下角发送IP地址,可直接编辑,右键从列表中选择
# 窗口标题传送文件进度条
# 发送消息为文件夹路径时,返回本机或对方文件列表
# 发送消息为文件路径时,发送或接收对应文件,重名增加序号后缀
# 允许使用相对路径(.\name)
# 上线广播,获取所有在线的聊天室IP,下线广播,通知移出列表
# 当无法加载GUI库时可作服务器运行,终端打印简略消息


# build 20210115


import os, sys
import time
import socket
import hashlib
from threading import Thread

# import traceback # for test

try:
    # raise # for test no tk-module
    tk = __import__('Tkinter' if sys.version_info[0] == 2 else 'tkinter')
except:
    print('Warning: import tk-module fail.')
    class TkFake:
        class Tk: pass
        class Menu: pass
        def __bool__(self): return False
    tk = TkFake()
    print('Warning: create fake tk-class.')

LOG  = 'log.txt'

HOST    = socket.gethostbyname(socket.gethostname()) # TODO Linux获取地址是127.0.0.1
# TODO 收到的REPEAT消息即为自己的IP地址? 无网线是否影响?
PORT    = 5009
BUFSIZE = 4096 # TODO 影响UDP消息最长字符(4096/3=1365)
CMD_LEN = 20   # MAX_LEN OF COMMAND LIKE 'SEND::'
TICK    = 0.5

__title__ = 'Chatroom (%s)'%HOST


class Progress:
    def __init__(self, info, file, total):
        self.info = info
        self.file = os.path.basename(file)
        self.total = total
        self.t = time.time()

    def __call__(self, size):
        if time.time() - self.t > TICK: # timer
            self.t = time.time()
            app.title('%s: %s (%.1f%%)'%(self.info, self.file, 100.0*size/self.total)) # py2不能强制类型转换所以用100.0


def UniqueFile(file): # Good!
    root, ext = os.path.splitext(file)
    cnt = 1
    while os.path.exists(file):
        file = b'%s_%d%s'%(root, cnt, ext)
        cnt += 1
    return file


def TcpSendFile(file, addr): # <file> can be with dirs
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((addr, PORT))

    # send file name
    file2 = file.encode('u8')
    file3 = os.path.basename(file2) # send filename without dir # win和linux的文件路径分隔符不一样可能导致错误
    client.send(file3)
    client.recv(BUFSIZE)
    # send file size
    size = os.path.getsize(file2)
    client.send(str(size).encode())
    client.recv(BUFSIZE)

    prog = Progress('Sending', file, size) # progress bar
    with open(file2, 'rb') as f:
        for n in range(0, size, BUFSIZE):
            client.send(f.read(BUFSIZE))
            prog(n+BUFSIZE) # progress bar # 保证了此处传参一定!=0

    client.close()

    return size, file3.decode('u8')


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

    file2 = UniqueFile(file)
    prog = Progress('Recving', file2.decode('u8'), size2) # progress bar
    with open(file2, 'wb') as f:
        while size: # 空文件也会传送(测试通过)
            block = client.recv(BUFSIZE)
            f.write(block)
            size -= len(block)
            prog(size2-size) # progress bar # 保证了此处传参一定!=0

    client.close()
    server.close()

    return size2, file2.decode('u8')


def LogFile(s=''): # Good!
    with open(LOG, 'ab+') as f:
        f.write(s.encode('u8'))
        f.seek(0)
        return f.read().decode('u8')


def Dispatch(u, cmd, msg, addr):
    # 前缀 SEND RECV BOOT ROBO ECHO AUTO FILE EROR
    app.addrs.add(addr) # TODO 是否要排除自己?
    if cmd in ['SEND', 'RECV']:
        app.Log('RECV', addr, msg)
    elif cmd == 'ECHO':
        app.Log('ECHO', addr, msg)
    if app:
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
                s = s.decode('u8') # Linux py27: str to unicode
                u.SendCmd('ACK1', s)
        if result:
            ss = b'\n'.join(result) # use b'\n' for next line
            ss = ss.decode('u8') # Linux py27: str to unicode
            if cmd == 'RECV':
                u.SendCmd('ECHO', ss)
            app.Log('ECHO', HOST, ss)

    elif cmd == 'ACK1':
        u.SendCmd('ACK2', msg)
        size, file = TcpRecvFile()
        app.Log('FILE', addr, 'Recved: %s (%d)'%(file, size)) # 先接收文件后记录log
        app.title(__title__)

    elif cmd == 'ACK2':
        app.Log('FILE', HOST, 'Sending: %s'%msg) # 发送的文件是带路径的(msg),接收的文件是不带路径的(file)
        size, file = TcpSendFile(msg, addr) # 先记录log后发送文件
        app.title(__title__)

    elif cmd == 'BROC':
        if msg == 'ONLINE':
            u.SendCmd('BROC', 'REPEAT')
        elif msg == 'OFFLINE':
            if addr in app.addrs:
                app.addrs.remove(addr)


def Receiver(u):
    def th():
        while RUN:
            cmd, msg, addr = u.RecvCmd()
            # print((cmd, msg, addr)) # for test
            try:
                Dispatch(u, cmd, msg, addr)
            except Exception as e:
                app.Log('EROR', addr, e)
                # raise e # for test
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


class MyAppFake(tk.Tk):
    def __init__(self):
        self.addrs = {'localhost'}

    def __bool__(self):
        return False

    def title(self, msg):
        print(msg.encode('u8')) # Linux: print(str) always fail

    def Log(self, typ, ip, msg):
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        s = '%s %s %s\n%s\n\n'%(typ, ip, t, msg)
        LogFile(s)
        print(s.encode('u8'))


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

        self.title(__title__)
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
    if tk:
        app = MyApp()
    else:
        app = MyAppFake()  # when tk-lib could not used
        print('Warning: create fake app.')
    u.Broadcast('ONLINE')

    if app:
        app.mainloop()
        app = MyAppFake() # window closed
        RUN = False
        u.Broadcast('OFFLINE')
        u.close()
