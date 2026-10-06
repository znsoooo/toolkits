import os
import socket
import struct
import hashlib


IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'heic', 'heif', 'tiff', 'ico', 'avif']
VIDEO_EXTS = ['mp4', 'mkv', 'mov', 'avi', '3gp', 'webm', 'flv', 'm4v', 'mpg', 'mpeg']

MEDIA_EXTS = IMAGE_EXTS + VIDEO_EXTS   # 图片 + 视频，供客户端遍历使用


class Tcp:
    def __init__(self, addr, port):
        self.host = not addr
        self.addr = addr
        self.port = port
        self.connect()

    def connect(self):
        if self.host:
            self.server = socket.socket()
            self.server.bind(('', self.port))
            self.server.listen(5)
            self.client, (addr, port) = self.server.accept()
        else:
            self.client = socket.socket()
            self.client.connect((self.addr, self.port))

    def close(self):
        self.client.close()
        if self.host:
            self.server.close()

    def send(self, data):
        data = data.encode() if isinstance(data, str) else data
        self.client.sendall(data)

    def recv(self, length):
        return self.client.recv(length)

    def sendlong(self, data):
        data = data.encode() if isinstance(data, str) else data
        assert len(data) < 1 << 32  # max 4GB
        self.send(struct.pack('I', len(data)) + data)

    def recvlong(self):
        length = struct.unpack('I', self.recv(4))[0]  # max 4GB
        data = bytearray()
        while len(data) < length:
            chunk = self.client.recv(length - len(data))
            if not chunk:
                raise ConnectionError
            data.extend(chunk)
        return bytes(data)

    def sendfile(self, path, size, chunk=1<<20):
        sent = 0
        with open(path, 'rb') as f:
            while sent < size:
                data = f.read(chunk)
                if not data:
                    break
                self.send(data)
                sent += len(data)

    def recvfile(self, path, size):
        received = 0
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'wb') as f:
            while received < size:
                chunk = self.recv(size - received)
                f.write(chunk)
                received += len(chunk)


class File:
    def __init__(self, path: str):
        self.path = os.path.normpath(path).replace(os.sep, '/')
        self.dir, self.basename = os.path.split(self.path)
        self.stem, self.ext = os.path.splitext(self.basename)
        self.info = {}

    @property
    def size(self) -> int:
        if 'size' not in self.info:
            self.info['size'] = os.path.getsize(self.path)
        return self.info['size']

    @property
    def md5(self) -> str:
        if 'md5' not in self.info:
            h = hashlib.md5()
            with open(self.path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            self.info['md5'] = h.hexdigest()
        return self.info['md5']

    @property
    def mtime(self) -> float:
        if 'mtime' not in self.info:
            self.info['mtime'] = os.path.getmtime(self.path)
        return self.info['mtime']

    @mtime.setter
    def mtime(self, value: float):
        os.utime(self.path, (os.path.getatime(self.path), value))
        self.info['mtime'] = value

    def __repr__(self) -> str:
        return f"File('{self.path}')"

    def __str__(self) -> str:
        return self.path


def LocalIps():
    """返回本机所有可用 IPv4 地址列表"""
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ips.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    for info in socket.getaddrinfo(socket.gethostname(), None):
        ip = info[4][0]
        if ':' not in ip and ip != '127.0.0.1' and ip not in ips:
            ips.append(ip)
    return ips


def PrintLocalIps():
    """打印本机所有可用 IPv4，便于手机端填服务器地址"""
    print('本机 IP:')
    for ip in LocalIps():
        print(f'  {ip}')


def Walk(paths, exts=('',), hidden=True):
    exts = tuple(ext.lower() for ext in exts)
    for path in paths:
        for root, folders, files in os.walk(path):
            if not hidden:
                folders[:] = [folder for folder in folders if not folder.startswith('.')]
                files[:] = [file for file in files if not file.startswith('.')]
            folders.sort()
            files.sort()
            for file in files:
                if file.lower().endswith(exts):
                    yield File(os.path.join(root, file))


def HumanSize(n: int) -> str:
    """字节数可读化：B-PB"""
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}'
        n /= 1024
    return f'{n:.1f} PB'


def PrintSummary(st):
    """两端统一的收尾统计：发送/跳过的文件个数与总大小"""
    print('-' * 40)
    print('完成传输:')
    print(f"  发送 {st['sent']} 个文件，总共 {HumanSize(st['sent_size'])}")
    print(f"  跳过 {st['skip']} 个文件，总共 {HumanSize(st['skip_size'])}")


def RelpathOf(path: str, roots) -> str:
    """算出 path 相对其所属 root 的相对路径，便于对端还原目录结构"""
    p = path.replace('\\', '/')
    for r in roots:
        rr = r.replace('\\', '/').rstrip('/')
        if p == rr or p.startswith(rr + '/'):
            rel = p[len(rr) + 1:] or os.path.basename(p)
            return (os.path.basename(rr) + '/' + rel).replace('\\', '/')
    return os.path.basename(path)
