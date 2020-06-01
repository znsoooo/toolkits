# 20191224 build
# 将压入文件信息存入8位深图片各像素的后4位并保存为PNG格式
# 生成后自动检测生成的图片文件可否正确抽出压入文件

# 20200530
# numpy加速(测试压入8.75MB文件: 74.86s -> 597ms)
# 压入数据中的前4字节记录文件的大小(最大支持4GB文件)
# 支持将图片转为4通道16位深的PNG文件(后8位为数据)，图片直观差异更小，但有图片浏览器查看兼容风险

# 20200601
# 支持中文路径的图片名(速度变慢1倍左右)
# 打印数据和图片像素数的利用情况，方便调整图片合适的大小
# 提供4种图片未利用像素区的处理方法(不变/置零/随机/重复)，达到比较一致的全图预览效果
# 自动扩大缩小图片以使图片面积利用率接近100%

# TODO
# 批量压入文件/多张图片
# 存入文件名
# 另一种策略: 文件长度大于图片尺寸时生成多图片


import cv2
import numpy as np


def AutoCheck(packfile, fromfile, deep16=False):
    from_data = ExtractFromFile(fromfile, deep16=deep16)
    pack_data = np.fromfile(packfile, np.uint8)
    return (pack_data == from_data).all()


def PressInFile(basefile, packfile, deep16=False, resize=False):
    # img = cv2.imread(basefile, cv2.IMREAD_UNCHANGED)
    img = cv2.imdecode(np.fromfile(basefile, dtype=np.uint8), -1)
    if deep16:
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        if img.dtype == np.uint8:
            img = img.astype(np.uint16) << 8

    data = np.fromfile(packfile, np.uint8)

    if resize:
        ratio = (2*len(data)/img.size)**0.5
        if deep16:
            ratio *= 0.5**0.5
        img = cv2.resize(img, (1+int(ratio*img.shape[1]), 1+int(ratio*img.shape[0])), interpolation=cv2.INTER_CUBIC)

    img1 = img.reshape(img.size)
    length = len(data)
    data_len = np.frombuffer(np.uint32(length).tobytes(), np.uint8) # length最大支持2**32=42e8
    data = np.append(data_len, data)
    if not deep16:
        data = np.vstack(divmod(data, 16)).T.reshape(-1) # 2xN矩阵转置后reshape达到原矩阵的两行错位插缝合并的效果
    # if len(img1) < len(data):
    print('Info: You can scale (%.2f%%) of image size %s to press in data (%s).'%(100*(len(data)/len(img1))**0.5, img.shape, len(data)))

    # fill mode
    # data = np.append(data, np.zeros(len(img1) - len(data), np.uint8)) # fill zero
    data = np.append(data, (np.random.random_sample(len(img1) - len(data)) * 16).astype(np.uint8)) # fill random
    # data = np.append(data, img1[len(data):]) # fill original
    # data = np.tile(data, 1+int(len(img1)/len(data)))[:len(img1)] # fill data self

    if deep16:
        img2 = img1 & 0xFF00 | data
    else:
        img2 = img1 & 0xF0 | data
    img2 = img2.reshape(img.shape)

    savefile = basefile + '.png' # 防止重名且锁定为png格式
    # cv2.imwrite(savefile, img2)
    cv2.imencode('.png', img2)[1].tofile(savefile)
    ret = AutoCheck(packfile, savefile, deep16=deep16)
    print('AutoCheck: %s'%ret)

    return img2, length


def ExtractFromFile(fromfile, savefile=None, deep16=False):
    # img = cv2.imread(fromfile, cv2.IMREAD_UNCHANGED)
    img = cv2.imdecode(np.fromfile(fromfile, dtype=np.uint8), -1)

    if deep16:
        data = img.reshape(img.size) & 0x00FF
        data = data.astype(np.uint8)
    else:
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
deep16 = 0 # True/Flase
PressInFile('image1.png', 'passage_all.rar', deep16=deep16, resize=1)
##PressInFile('中文1.png', 'passage_all.rar', deep16=deep16)
print(time.time() - t)
ExtractFromFile('image1.png.png', 'test.rar', deep16=deep16)
