# build 20200621

# 20200621
# 自动检测文件名
# 视频读取测试成功(传送224KB文件)

# 20200819
# 多线程加速


import base64
from threading import Thread

import cv2
from pyzbar import pyzbar


th_max = 10 # 最大线程数

th_arr = [] # 运行中线程
th_fin = [] # 已完成线程


class MyThread(Thread):
    def __init__(self, func, args=()):
        Thread.__init__(self)
        self.func = func
        self.args = args
        self.start()

    def run(self):
        self.result = self.func(*self.args)
        th_fin.append(self) # 先append后remove防止接力失败时两个数组均为空(尾部程序判断时误判)
        th_arr.remove(self)


def Zoom(img, ratio):
    img_small = cv2.resize(img, (int(img.shape[1]*ratio), int(img.shape[0]*ratio)), interpolation=cv2.INTER_NEAREST)
    return img_small


def ReadVideo(cap):
    cnt = 0
    while 1:
        ret, img = cap.read()
        if not ret:
            cap.release()
            break
        cnt += 1
        yield img


def ScanQrcode(img, blur=0, show=0):
    if blur:
        img = cv2.blur(img, (blur, blur))
    if show:
        cv2.imshow('', Zoom(img, 0.2))
        cv2.waitKey(1)
    datas = pyzbar.decode(img)
    datas = sorted([data.data.decode() for data in datas if data.type=='QRCODE']) # 有时二维码会读出一个几位的数字来
    # print('datas:', len(datas))
    # for data in datas:
    #     print('%4d'%len(data), data.__repr__()[:60])
    # print('blur: %s, read: %s\n'%(blur, len(datas)), end='')
    return datas


def AddStrings(arr, ss):
    for s in ss:
        cnt = int(s[:5])
        if len(arr) < cnt:
            arr += [''] * (cnt - len(arr))
        if cnt > 0: # 起始位没有信息
            arr[cnt-1] = s


def ExportFile(datas):
    s = ''.join(data[6:] for data in datas)
    s1 = base64.b64decode(s)
    s2, s3 = s1.split(b'\n', 1)
    file = s2.decode()
    with open('recv_file/' + file, 'wb') as f:
        f.write(s3)

    brief = s3[:20] + b'.........' + s3[-20:]
    print('Write File:', file)
    print('Write Data:', brief)


def ExtrctVideo(file, skip=0, jump=0):
    cap = cv2.VideoCapture(file)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    result = []
    for n, img in enumerate(ReadVideo(cap)):
        if n < skip: # skip to body
            continue
        if n % jump: # 适当跳帧提高速度
            continue

        for blur in range(0, 10, 2):

            while len(th_arr) >= th_max:
                pass
            th_arr.append(MyThread(ScanQrcode, (img, blur)))

            while th_fin:
                AddStrings(result, th_fin.pop().result)

        total = length - skip
        now   = n + 1  - skip
        print('Read: %d/%d, Elapsed: %.1fs, Remaining: %.1fs, Success: %d/%d'%(now, total, time.clock(), time.clock()*(total/now-1),
                                                                               len(result)-result.count(''), len(result)))

        if n % 20 == 0:
            with open('log.txt', 'w') as f:
                f.write('\n'.join(result))

    while th_arr or th_fin:
        if th_fin:
            AddStrings(result, th_fin.pop().result)

    with open('log.txt', 'w') as f:
        f.write('\n'.join(result))

    print('length:', len(result))
    print('empty:',  result.count(''))

    return result


import time

time.clock()
file = 'video_20200819_075554.mp4'
video_datas = ExtrctVideo(file, skip=200, jump=8) # skip to body, jump for frameskip
ExportFile(video_datas)
print('Time:', time.clock())


## 测试数据
# 视频: 29s/30fps
# 单线程：43分钟
# 10线程: 572.85s
# 10线程(skip 80帧): 494.16s
# 20线程(skip 80帧): 425.91s
# 10线程(skip 80帧, 8倍跳帧): 69.09s
# 10线程(skip 200帧, 8倍跳帧): 60.76s

