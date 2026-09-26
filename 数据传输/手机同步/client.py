import util


# ----- 配置区 -----

SERVER_PORT = 9000

WALK_ROOTS = [
    'phone',
    '/storage/emulated/0/DCIM',
    '/storage/emulated/0/Pictures',
    # '/storage/emulated/0/Movies',
    # '/storage/emulated/0/Download',
]

CHUNK = 1 << 20  # 分块 1MB

# ----- 配置区 -----


def SendFile(tcp, path: str, size: int, chunk: int = CHUNK):
    """按 size 字节流式发送内容，1MB/次"""
    sent = 0
    with open(path, 'rb') as f:
        while sent < size:
            data = f.read(chunk)
            if not data:
                break
            tcp.send(data)
            sent += len(data)


def main():
    port, roots = SERVER_PORT, WALK_ROOTS
    util.PrintLocalIps()

    host = input('请输入PC端IP地址: ').strip()

    print(f'连接 {host}:{port} ...')
    tcp = util.Tcp(host, port)

    st = {'sent_size': 0, 'sent': 0, 'skip': 0, 'skip_size': 0}

    for file in util.Walk(roots, exts=util.MEDIA_EXTS, hidden=False):
        if file.size == 0:
            continue

        tcp.sendlong('FILE')
        relpath = util.RelpathOf(file.path, roots)

        tcp.sendlong(relpath)
        tcp.sendlong(str(file.size))
        tcp.sendlong(file.md5)

        cmd = tcp.recvlong().decode()

        if cmd == 'SKIP':
            st['skip'] += 1
            st['skip_size'] += file.size
            print(f'跳过: {relpath} ({util.HumanSize(file.size)})')
        elif cmd == 'DATA':
            SendFile(tcp, file.path, file.size)
            tcp.sendlong(str(file.mtime))
            st['sent'] += 1
            st['sent_size'] += file.size
            print(f'发送: {relpath} ({util.HumanSize(file.size)})')
        else:
            raise ValueError(cmd)

    tcp.sendlong('END')
    util.PrintSummary(st)


if __name__ == '__main__':
    main()
