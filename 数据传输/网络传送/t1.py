from transfer import *

Thread(target=TcpRecvFile).start()
TcpSendFile('demo.zip', HOST)
print('Fin.')
