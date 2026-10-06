import time

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

# ----- 配置区 -----

def InputDays():
    text = input('同步最近多少天的文件: ').strip()
    return int(text) if text else 0


def InputHost(default=''):
    host = input('请输入PC端IP地址: ').strip()
    tail = host.split('.') if host else []
    head = default.split('.') if default else []
    return '.'.join(head[:max(0, 4 - len(tail))] + tail)


def main():
    port, roots = SERVER_PORT, WALK_ROOTS
    ips = util.LocalIps()
    local_ip = ips[0] if ips else ''
    util.PrintLocalIps()

    host = InputHost(local_ip)
    days = InputDays()
    deadline = time.time() - days * 86400   # 仅同步 mtime >= deadline 的文件；days=0 时不过滤

    print(f'连接 {host}:{port} ...')
    tcp = util.Tcp(host, port)

    st = {'sent_size': 0, 'sent': 0, 'skip': 0, 'skip_size': 0}

    for file in util.Walk(roots, exts=util.MEDIA_EXTS, hidden=False):
        if file.size == 0:
            continue
        if days and file.mtime < deadline:
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
            tcp.sendfile(file.path, file.size)
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
