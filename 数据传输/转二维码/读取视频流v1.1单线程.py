# build 20200621

# 20200621
# 自动检测文件名
# 视频读取测试成功(传送224KB文件)


import base64

import cv2
from pyzbar import pyzbar


CNT_IN_FRAME = 18


def Zoom(img, ratio):
    img_small = cv2.resize(img, (int(img.shape[1]*ratio), int(img.shape[0]*ratio)), interpolation=cv2.INTER_NEAREST)
    return img_small


def ReadVideo(file, skip=0):
    cap = cv2.VideoCapture(file)
    cnt = 0
    while 1:
        ret, img = cap.read()
        if not ret:
            cap.release()
            break
        cnt += 1
        if cnt > skip:
            yield img


def ScanQrcode(img, show=0):
    if show:
        cv2.imshow('', Zoom(img, 0.2))
        cv2.waitKey(1)
    datas = pyzbar.decode(img)
    datas = sorted([data.data.decode() for data in datas if data.type=='QRCODE']) # 有时二维码会读出一个几位的数字来
    # print('datas:', len(datas))
    # for data in datas:
    #     print('%4d'%len(data), data.__repr__()[:60])
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


def ExtrctVideo(file):
    result = []
    for n, img in enumerate(ReadVideo(file)):
        for k in range(0, 10, 2):
            if k == 0:
                img_blur = img
            else:
                img_blur = cv2.blur(img, (k, k))
            datas = ScanQrcode(img_blur)
            AddStrings(result, datas)
            print('frame: %s, blur: %s, read: %s'%(n, k, len(datas)))
            if len(datas) == CNT_IN_FRAME:
                break

        # if n % 20 == 0:
        #     with open('log.txt', 'w') as f:
        #         f.write('\n'.join(result))

    with open('log.txt', 'w') as f:
        f.write('\n'.join(result))

    print('length:', len(result))
    print('empty:',  result.count(''))

    return result


file = 'video_20200819_075554.mp4'
video_datas = ExtrctVideo(file)
ExportFile(video_datas)
