import socket
import optparse

parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='')
parser.add_option('-p', dest='port', type='int', default=12345)
parser.add_option('-m', dest='msg', default='Hello World!')
(options, args) = parser.parse_args()

# 创建 socket 对象
serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM) 

# 获取本地主机名
# host = socket.gethostname()

# port = 9999

# 绑定端口号
serversocket.bind((options.ip, options.port))

# 设置最大连接数，超过后排队
serversocket.listen(5)

while True:
    # 建立客户端连接
    clientsocket,addr = serversocket.accept()      

    print("连接地址: %s" % str(addr))
    
    # msg='Hello World!'+ "\r\n"
    clientsocket.send(options.msg.encode('utf-8'))
    clientsocket.close()