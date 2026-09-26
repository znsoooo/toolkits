import os
import time

import util


# ----- 配置区 -----

SERVER_PORT = 9000

# 预扫描的根目录；索引即在这些目录里查重
SERVER_SCAN_ROOTS = [
    r'.',
    r'pc',
    # r'D:\Pictures',
    # r'D:\Videos',
    # r'E:\Photos',
]

# 接收文件落盘目录: "日期_时间" 文件夹 (如 "20260930_123000")
NEW_DIR = time.strftime('%Y%m%d_%H%M%S')

# ----- 配置区 -----


def BuildDatabase(roots):
    database = list(util.Walk(roots))
    print(f'已扫描本机文件 {len(database)} 个，建立索引完成。')
    return database


def UniquePath(path):
    root, ext = os.path.splitext(path)
    i = 2
    while os.path.exists(path):
        path = f'{root}_{i}{ext}'
        i += 1
    return path


def RecvFile(tcp, relpath: str, size: int):
    """把客户端发来的内容落盘到 <落盘目录>/<相对路径>，还原文件最后修改时间"""
    file = util.File(UniquePath(os.path.join(NEW_DIR, relpath)))
    os.makedirs(file.dir, exist_ok=True)
    with open(file.path, 'wb') as f:
        received = 0
        while received < size:
            chunk = tcp.recv(size - received)
            f.write(chunk)
            received += len(chunk)
    file.mtime = float(tcp.recvlong())


def RecvFiles(tcp, database):
    st = {'sent': 0, 'sent_size': 0, 'skip': 0, 'skip_size': 0}

    while True:
        cmd = tcp.recvlong().decode()
        if cmd == 'END':
            break

        relpath = tcp.recvlong().decode()
        basename = os.path.basename(relpath)
        size = int(tcp.recvlong())
        md5 = tcp.recvlong().decode()

        for file in database:
            if file.basename == basename and file.size == size and file.md5 == md5:
                tcp.sendlong('SKIP')
                st['skip'] += 1
                st['skip_size'] += size
                print(f'跳过: {relpath} ({util.HumanSize(size)})')
                break
        else:
            tcp.sendlong('DATA')
            RecvFile(tcp, relpath, size)
            st['sent'] += 1
            st['sent_size'] += size
            print(f'接收: {relpath} ({util.HumanSize(size)})')

    util.PrintSummary(st)


def main():
    util.PrintLocalIps()

    database = BuildDatabase(SERVER_SCAN_ROOTS)
    print(f'等待手机连接...')

    tcp = util.Tcp(None, SERVER_PORT)
    RecvFiles(tcp, database)


if __name__ == '__main__':
    main()
