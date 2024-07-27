# Author: Li Shixian
# Update: 2024-07-23
# SendTo: shell:sendto


import os
import os.path as osp
import sys
import ftplib
import shutil
import traceback


def AddSendTo():
    if not sys.platform == 'win32':
        return
    try:
        src = __file__
        dst = osp.expandvars('%APPDATA%/Microsoft/Windows/SendTo/') + osp.basename(__file__)
        if not osp.exists(dst) or not osp.samefile(src, dst):
            shutil.copy(src, dst)
    except Exception:
        traceback.print_exc()


def UploadFtp(path, cwd='/'):
    ftp = ftplib.FTP()
    ftp.encoding = 'utf-8'
    ftp.connect('110.110.0.176', 55610)
    ftp.login('shiyan-6shi-zczc', 'shi!2394@78239yan#')

    ftp.cwd(cwd)
    ftp.set_pasv(False)
    ftp.sendcmd('TYPE I')

    basename = os.path.basename(path)
    with open(path, 'rb') as f:
        ftp.storbinary('STOR {}'.format(basename), f)

    ftp.quit()


def main():
    paths = [path for path in sys.argv[1:] if osp.isfile(path)]
    if not len(paths):
        return

    print('总共 {} 个文件, 在提示 "完成" 前请勿关闭窗口:'.format(len(paths)))
    print()

    count = 0
    for i, path in enumerate(paths, 1):
        try:
            print('上传中: "{}" ({}) '.format(osp.basename(path), osp.getsize(path)), end='', flush=True)
            UploadFtp(path, cwd='/auto')
            count += 1
            print('(成功)')
        except Exception as e:
            print('(失败: {})'.format(e))

    print()
    print('完成上传 {} 个文件, 请在FTP的 "auto" 文件夹中查看结果.'.format(count))
    input()


if __name__ == '__main__':
    AddSendTo()
    main()
