import socket, optparse

parser = optparse.OptionParser()
parser.add_option('-i', dest='ip', default='127.0.0.1')
parser.add_option('-p', dest='port', type='int', default=12345)

(options, args) = parser.parse_args()

# 创建 socket 对象
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# 获取本地主机名
# host = socket.gethostname() 

# 设置端口号
# port = 9999

# 连接服务，指定主机和端口
s.connect((options.ip, options.port))


f = open('foo.txt','w')

# 接收小于 1024 字节的数据
msg = s.recv(1024)

s.close()

f.write("%s\n" % (msg.decode('utf-8')))
f.flush()
# print (msg.decode('utf-8'))