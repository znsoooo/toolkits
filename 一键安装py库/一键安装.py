# build 20200818_fix1

import os
import zipfile
import tarfile

delay_cmd = ' && choice /t 2 /d y /n >nul' # delay 2s to watch result.

def install(path):
    cwd = os.getcwd()
    path = os.path.abspath(path)
    root, file = os.path.split(path)
    os.chdir(root)
    filename, ext = os.path.splitext(file)
    ext = ext.lower()
    if ext == '.gz':
        f = tarfile.open(path)
        f.extractall()
        folder = f.getnames()[0]
        os.chdir(folder)
        os.system('python setup.py install' + delay_cmd)
    elif ext == '.zip':
        f = zipfile.ZipFile(path)
        f.extractall()
        folder = f.namelist()[0].split('/')[0]
        os.chdir(folder)
        os.system('python setup.py install' + delay_cmd)
    elif ext == '.whl':
        os.system('pip install "%s"'%path + delay_cmd)
    os.chdir(cwd)


cwd = os.getcwd()
for folder in os.listdir():
    if os.path.isdir(folder):
        for file in os.listdir(folder):
            install(os.path.join(folder, file))

