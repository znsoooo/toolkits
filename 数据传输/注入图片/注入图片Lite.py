# 20200601 Make Lite

import cv2
import numpy as np


def AutoCheck(packfile, fromfile):
    from_data = ExtractFromFile(fromfile)
    pack_data = np.fromfile(packfile, np.uint8)
    return (pack_data == from_data).all()


def PressInFile(basefile, packfile):
    img = cv2.imread(basefile, cv2.IMREAD_UNCHANGED)

    img1 = img.reshape(img.size)
    data = np.fromfile(packfile, np.uint8)
    length = len(data)
    data_len = np.frombuffer(np.uint32(length).tobytes(), np.uint8) # length最大支持2**32=42e8
    data = np.append(data_len, data)
    data = np.vstack(divmod(data, 16)).T.reshape(-1) # 2xN矩阵转置后reshape达到原矩阵的两行错位插缝合并的效果
    print('Info: You can scale (%.2f%%) of image size %s to press in data (%s).'%(100*(len(data)/len(img1))**0.5, img.shape, len(data)))

    data = np.append(data, img1[len(data):]) # fill original

    img2 = img1 & 0xF0 | data
    img2 = img2.reshape(img.shape)

    savefile = basefile + '.png' # 防止重名且锁定为png格式
    cv2.imwrite(savefile, img2)
    ret = AutoCheck(packfile, savefile)
    print('AutoCheck: %s'%ret)

    return img2, length


def ExtractFromFile(fromfile, savefile=None):
    img = cv2.imread(fromfile, cv2.IMREAD_UNCHANGED)

    data = img.reshape(img.size) & 0x0F
    data = data.reshape((-1, 2)).T
    data = (data[0] << 4) + data[1]
    data_len = data[:4]
    length = np.frombuffer(np.uint8(data_len).tobytes(), np.uint32)[0]
    data = data[4:4+length]

    if savefile:
        data.tofile(savefile)

    return data



import time
t = time.time()
PressInFile('image1.png', 'passage_all.rar')
print(time.time() - t)
ExtractFromFile('image1.png.png', 'test.rar')
