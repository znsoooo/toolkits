import os
import sys
import ftplib
import traceback


def UploadFtp(path, cwd='/'):
    print('Uploading: "{}"'.format(path))

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


if __name__ == '__main__':
    try:
        for path in sys.argv[1:]:
            UploadFtp(path, cwd='/auto')
    except Exception:
        traceback.print_exc()
    finally:
        os.system('pause')
