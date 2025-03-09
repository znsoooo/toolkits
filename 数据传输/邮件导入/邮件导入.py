"""
使用方法：
    安装Python 3.6以上的版本
    Win+R打开启动，输入<shell:sendto>(不含尖括号)，回车运行
    右键新建快捷方式，输入<py "本文件路径.py">(不含尖括号)，注意加空格和引号，文件路径要含有后缀名
    推荐将快捷方式命名为"邮件导入"
    然后就可以在文件浏览器内多选文件、使用右键"发送到"进行快速摆渡邮件导入了
    注意邮件总大小不可超过50MB
    可以根据需要自行修改代码

"""

import os
import sys
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header

paths = sys.argv[1:]

send_addr = 'calt12060102@126.com'
pass_word = 'JBUZLVIWSODRQFDU'    # 'AB12345678c'
recv_addr = 'wai2nei@vip.163.com' # 'wai2nei@vip.163.com'
smtp_server = 'smtp.126.com'

subject = 'lishx1'  # input('输入邮箱主题: ').lower().strip()
body = f'\nThis email contain {len(paths)} attachments:\n' + ''.join(f'  "{p}"\n' for p in paths)
print(body)

msg = MIMEMultipart()
msg['Subject'] = Header(subject, 'utf-8')
msg['From'] = send_addr
msg['To'] = recv_addr
msg.attach(MIMEText(body, 'plain', 'utf-8'))

for path in paths:
    if os.path.exists(path):
        with open(path, 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
            msg.attach(attachment)

try:
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.login(send_addr, pass_word)
    server.sendmail(send_addr, recv_addr, msg.as_string())
    server.quit()
except Exception as e:
    traceback.print_exc(1)
    print()
else:
    print('Send success!\n')

os.system('pause')
