import socket
import sys

# 创建 socket 对象
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# 获取本地主机名
host = socket.gethostname() 

# 设置端口号
port = 8000

# 连接服务，指定主机和端口
s.connect((socket.gethostname() , 8000))

# while True:
#     # 接收小于 1024 字节的数据
#     msg = s.recv(1024)
#     print (msg.decode('utf-8'))
s.send("D1".encode('utf8'))

