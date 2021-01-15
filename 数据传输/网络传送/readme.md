## V1 send.py - recv.py
- 发送64KB以内的文件

## V2 server.py - client.py
- 发送任意大小的文件，先启动server后启动client。
- client是UI交互界面，可以发送和接收文件。

## V3 transfer.py
- 两台电脑均可单独启动，发送给指定IP地址消息或传送文件。发送消息用UDP，发送文件用TCP。
- 当交互界面（tkinter）库不存在时，可单独调用TcpSendFile和TcpRecvFile函数收发文件（先运行TcpRecvFile）。

## TODO chatroom.py
- 支持聊天记录、获取文件列表、获取IP列表、广播发送、发送多行文本
