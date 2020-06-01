# 20191224 build
# 将压入文件信息存入8位深图片各像素的后4位并保存为PNG格式
# 生成后自动检测生成的图片文件可否正确抽出压入文件

# 20200530
# numpy加速(测试压入8.75MB文件: 74.86s -> 597ms)
# 压入数据中的前4字节记录文件的大小(最大支持4GB文件)
# 支持将图片转为4通道16位深的PNG文件(后8位为数据)，图片直观差异更小，但有图片浏览器查看兼容风险

# TODO
# 中文路径的图片名
# 数据超出图片像素数时的保护或处理方法
# 可设置的'未利用像素区'的处理方法(不变/置零/随机)，达到比较一致的全图预览效果 np.random.randn(4,3)



import cv2
import numpy as np


def AutoCheck(packfile, fromfile, deep16=False):
    from_data = ExtractFromFile(fromfile, deep16=deep16)
    pack_data = np.fromfile(packfile, np.uint8)
    return (pack_data == from_data).all()


def PressInFile(basefile, packfile, deep16=False):
    img = cv2.imread(basefile, cv2.IMREAD_UNCHANGED)
    if deep16:
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        if img.dtype == np.uint8:
            img = img.astype(np.uint16) << 8
    img1 = img.reshape(img.size)

    data = np.fromfile(packfile, np.uint8)
    length = len(data)
    data_len = np.frombuffer(np.uint32(length).tobytes(), np.uint8) # length最大支持2**32=42e8
    data = np.append(data_len, data)
    if not deep16:
        data = np.vstack(divmod(data, 16)).T.reshape(-1) # 2xN矩阵转置后reshape达到原矩阵的两行错位插缝合并的效果
    data = np.append(data, np.zeros(len(img1) - len(data), np.uint8))

    if deep16:
        img2 = img1 & 0xFF00 | data
    else:
        img2 = img1 & 0xF0 | data
    img2 = img2.reshape(img.shape)

    savefile = basefile + '.png' # 防止重名且锁定为png格式
    cv2.imwrite(savefile, img2)
    ret = AutoCheck(packfile, savefile, deep16=deep16)
    print('AutoCheck: %s'%ret)

    return img2, length


def ExtractFromFile(fromfile, savefile=None, deep16=False):
    img = cv2.imread(fromfile, cv2.IMREAD_UNCHANGED)

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
deep16 = 1 # True/Flase
PressInFile('image1.png', 'passage_all.rar', deep16=deep16)
print(time.time() - t)
ExtractFromFile('image1.png.png', 'test.rar', deep16=deep16)
