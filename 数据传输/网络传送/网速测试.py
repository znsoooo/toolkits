import socket
import struct


class Tcp:
    def __init__(self, addr='localhost', port=7010):
        self.host = not addr
        self.addr = addr
        self.port = port
        self.connect()

    def connect(self):
        if self.host:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('', self.port))
            self.server.listen(5)
            self.client, (addr, port) = self.server.accept()
        else:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.addr, self.port))

    def close(self):
        self.client.close()
        if self.host:
            self.server.close()

    def send(self, data):
        assert len(data) < 1 << 32  # max 4GB
        self.client.send(struct.pack('I', len(data)) + data)

    def recv(self, length=-1):
        if length == -1:
            length = struct.unpack('I', self.recv(4))[0]  # max 4GB
        s = bytearray()
        while len(s) < length:
            s.extend(self.client.recv(length-len(s)))
        return bytes(s)


if __name__ == '__main__':
    import time
    import random

    addr = input('Remote addr (empty for host): ')
    if addr and '.' not in addr:
        addr = '192.168.1.' + addr
    tcp = Tcp(addr)
    print('Connected:', addr or 'HOST')

    data = bytes(random.randint(0, 255) for i in range(1_000_000))
    data2 = b'A quick brown fox jump over the lazy dog.'
    length = len(data)
    print('Length:', length)

    t1 = time.time()
    tcp.send(data2) if addr else tcp.recv()
    t2 = time.time()
    tcp.recv() if addr else tcp.send(data2)
    t3 = time.time()
    print('Delay:', t2 - t1, t3 - t2)

    total = 0
    interval = 1
    t1 = time.time()
    while True:
        if addr:
            tcp.recv()
        else:
            tcp.send(data)

        t2 = time.time()
        total += length
        if t2 - t1 > interval:
            speed = total / (t2 - t1)
            print('Speed: {:>12,.0f} B/s'.format(speed))
            t1 = t2
            total = 0
