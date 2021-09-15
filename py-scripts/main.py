from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from topo import *
import copy
import json

import os

SELECT_TOPO = copy.deepcopy(Middleware_client_server)

CLIENT_NUMBER = 0
SERVER_NUMBER = 0
ROUTER_NUMBER = 0
SWITCH_NUMBER = CLIENT_NUMBER + SERVER_NUMBER + ROUTER_NUMBER

SERVER_THREAD = 10
CLIENT_THREAD = 10

START_PORT = 4433

switch = []
client = []
server = []
bw = {}
delay = {}
cpu = {}

def sendAndWait(host, line, send=True, debug=False):
    if not send:
        return ''
    # print('*** Executing cmd:', line)

    host.sendCmd(line)
    ret = host.waitOutput().strip()
    if ret != '' and debug:
        print(ret)
    return ret

def init():
    global CLIENT_NUMBER, SERVER_NUMBER, ROUTER_NUMBER, SWITCH_NUMBER, SERVER_THREAD, CLIENT_THREAD
    global bw, delay, cpu
    SERVER_NUMBER = SELECT_TOPO['server_number']
    CLIENT_NUMBER = SELECT_TOPO['client_number']
    ROUTER_NUMBER = SELECT_TOPO['router_number']
    SWITCH_NUMBER = SERVER_NUMBER + CLIENT_NUMBER + ROUTER_NUMBER
    SERVER_THREAD = SELECT_TOPO['server_thread']
    CLIENT_THREAD = SELECT_TOPO['client_thread']

    bw = SELECT_TOPO['bw']
    delay = SELECT_TOPO['delay']
    cpu = SELECT_TOPO['cpu']


def clear_logs():
    os.system("rm -f temp_*")
    os.system("bash ../bash-scripts/clear_logs.sh")
    os.system("bash ../bash-scripts/kill_running.sh")


def test_run(net):

    import time
    import random
    
    now_port = START_PORT
    for server_id in range(SERVER_NUMBER):
        server_ip = "10.0.%s.3" %(str(server_id))
        print("../ngtcp2-exe/start_server.sh -i %s -s %s -p %s -t %s"%(str(server_id), server_ip, str(now_port), str(SERVER_THREAD)))
        server[server_id].cmd("../ngtcp2-exe/start_server.sh -i %s -s %s -p %s -t %s"%(str(server_id), server_ip, str(now_port), str(SERVER_THREAD)))
        # server[server_id].cmd("LD_LIBRARY_PATH=~/data ~/data/server --interface=server%s-eth0 --unicast=10.0.%s.3 0.0.0.0 %s ~/data/server.key ~/data/server.crt -q 1> temp_server_%s_1.txt 2> temp_server_%s_2.txt &"%(str(server_id), str(server_id), str(4433+server_id), str(server_id), str(server_id)))
        now_port += SERVER_THREAD
    
    time.sleep(30)

    for client_id in range(CLIENT_NUMBER):
        server_id = random.randint(0, SERVER_NUMBER - 1)
        server_ip = "10.0.%s.3" %(str(server_id))
        now_port = START_PORT + server_id * SERVER_THREAD
        print("../ngtcp2-exe/start_client.sh -i %s -s %s -p %s -t %s"%(str(client_id), server_ip, str(now_port), str(CLIENT_THREAD)))
        client[client_id].cmd("../ngtcp2-exe/start_client.sh -i %s -s %s -p %s -t %s"%(str(client_id), server_ip, str(now_port), str(CLIENT_THREAD)))
        time.sleep(0.5)
        # client[client_id].cmd("LD_LIBRARY_PATH=~/data ~/data/client 10.0.%s.3 %s -i -p normal_1 -o 1 -w google.com --client_ip 10.0.0.1 --client_process %s --time_stamp 1234567890 -q 1> temp_client_%s_1.txt 2> temp_client_%s_2.txt &"%(str(server_id),str(4434+server_id*2),str(4434+server_id*2),str(client_id),str(client_id)))

 
def myNetwork(net):
    ''' 
        ip地址：
            client: 10.0.0.0/16
                    10.0.x.1 clientx ip
                    10.0.x.1 clientx->switch0 网卡
            server: 10.0.0.0/16
                    10.0.x.3 clientx ip
                    10.0.x.3 clientx->switch0 网卡
            
    '''


    print( '*** Add switches\n')
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addSwitch('switch%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone', stp=True)) ## 防止回路

    print( '*** Add hosts\n')
    print(cpu)
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('client%s'%str(client_id), cpu=cpu['client']/CLIENT_NUMBER, ip='10.0.%s.1'%str(client_id), defaultRoute=None)) ## cpu占用为 系统的x%/所有client数量
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('server%s'%str(server_id), cpu=cpu['server']/SERVER_NUMBER, ip='10.0.%s.3'%str(server_id), defaultRoute=None))
    
    print( '*** Add links\n')
    
    for client_id in range(CLIENT_NUMBER):
        net.addLink(switch[client_id], client[client_id])
    for server_id in range(SERVER_NUMBER):
        net.addLink(switch[CLIENT_NUMBER+server_id], server[server_id])

    ## 通过多次调用addlink，使得switch之间创建多个网关的链接关系

    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[client_id], switch[CLIENT_NUMBER+server_id], cls=TCLink, **{'bw':bw['client_server'][client_id][server_id],'delay':delay['client_server'][client_id][server_id]}) 
    
    print( '*** Starting network\n')
    net.build()
 
    print( '*** Starting switches\n')
    for switch_id in range(SWITCH_NUMBER):
        net.get('switch%s'%str(switch_id)).start([])
    ## 定义网卡
    
    for switch_id in range(SWITCH_NUMBER):
        switch[switch_id].cmd('sysctl -w net.ipv4.ip_forward=1')
   
    print( '*** Post configure switches and hosts\n')
    ## 对具体的网卡指定对应的ip
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd('ifconfig client%s-eth0 10.0.%s.1'%(str(client_id), str(client_id)))
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd('ifconfig server%s-eth0 10.0.%s.3'%(str(server_id), str(server_id)))

    ## client,server发出
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd("ip route add default dev client%s-eth0 proto kernel scope link"%(str(client_id)))  
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd("ip route add default dev server%s-eth0 proto kernel scope link"%(str(server_id)))  
    
 
if __name__ == '__main__':
    setLogLevel( 'info' )
    clear_logs()

    init()

    net = Mininet( topo=None,
                build=False,
                host=CPULimitedHost,
                ipBase='10.0.0.0/8',
                controller=None)

    myNetwork(net)
    ## 设置跑
    # test_run(net)
    CLI(net)
    net.stop()
