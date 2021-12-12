import os
import subprocess
import random
import time

exe = r'D:\迅雷下载\ACDSee QuickView\ACDSeeQuickView.exe'

folders = os.listdir('image')

##while(1):
folder = folders[random.randint(0, len(folders))]
print(folder)
cmd = r'"%s" "%s\image\%s\%s"'%(exe, os.getcwd(), folder, os.listdir('image/%s'%folder)[0])
os.popen(cmd)
##    subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)


##    time.sleep(1)
