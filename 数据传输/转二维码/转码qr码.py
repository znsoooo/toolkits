# build 20200620
# 标题栏展示当前位置/二维码总数/百分比/已运行时间/预估总时间/每秒帧率
# 后台生成qrcode可以适当加速生成速度(大约每秒可以生成60+副)
# 每幅二维码包含5位的数字编号信息用于日后恢复二进制信息
# 自动包含文件名
# 配套的读取视频流提取文件程序

# TODO
# 自动包含文件总长度
# 和qr码工具兼容
# 为什么如果二维码包含的直接是二进制信息(而不是base64)时用pyzbar库读取会失败

import time
import base64
import tkinter
from threading import Thread

import qrcode
from PIL import ImageTk


def qrmake(qrstr):
    qr = qrcode.QRCode(box_size=3, border=3)
    qr.add_data(qrstr)
    qr.best_fit() # start=20
    qr.makeImpl(False, 3) # 3 or 6
    img = qr.make_image()
    img2 = ImageTk.PhotoImage(image=img)
    return img2


def qrmake_thread(arr, s):
    def t1():
        arr[1] = qrmake(s)
        arr[0].config(image=arr[1])
    Thread(target=t1).start()


def readfile(top, qrcs, s, length):
    time.sleep(1.5)

    cnt_max = int(1+(len(s)-1)/length)
    print('cnt_max:', cnt_max)
    t = time.clock()

    step = len(qrcs)
    for i in range(0, cnt_max, step):
        time.sleep(0.05)
        t = time.clock()
        rate = (i+1)/cnt_max
        speed = (i+1)/(t*step)
        top.title('%d/%d %.2f%% %.1f/%.1fs %.1ffps'%(i+1, cnt_max, rate*100, t, t/rate, speed))
        for j in range(step):
            s2 = s[(i+j)*length:(i+j+1)*length]
            qrmake_thread(qrcs[j], '%05d:%s'%((i+j+1), s2))


def main(file, length, rows, cols):
    with open(file, 'rb') as f:
        s = file.encode() + b'\n' + f.read()
    s = base64.b64encode(s).decode()

    qrcs = []
    default_text = b'00000:' + b'az' * (length // 2) # 'az'填充的qr码和实际数据的二维码大小最接近，从而避免窗口忽然变化
    top = tkinter.Tk()
    for r in range(rows):
        for c in range(cols):
            qrc = tkinter.Label(top)
            img = qrmake(default_text)
            qrc.config(image=img)
            qrc.grid(row=r, column=c)
            qrcs.append([qrc, img])

    Thread(target=readfile, args=(top, qrcs, s, length)).start()
    top.mainloop()


if __name__ == '__main__':
    ##main('passage2019.rar', 256, 3, 6)
    main('test.rar', 256, 3, 6)

