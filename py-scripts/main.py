from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

import os

CLIENT_NUMBER = 20
SERVER_NUMBER = 20
ROUTER_NUMBER = 0
SWITCH_NUMBER = CLIENT_NUMBER + SERVER_NUMBER + ROUTER_NUMBER

switch = []
client = []
server = []

def clear_output():
    os.system("rm -f temp_*")


def test_run(net):

    import time
    import random
    
    # server[0].cmd("LD_LIBRARY_PATH=~/data ~/data/server --interface=server0-eth0 --unicast=10.0.0.3 0.0.0.0 4443 ~/data/server.key ~/data/server.crt -q 1> temp_server1.txt 2> temp_server2.txt &")
    # time.sleep(30)
    # client[0].cmd("LD_LIBRARY_PATH=~/data ~/data/client 10.0.0.3 4443 -i -p normal_1 -o 1 -w google.com --client_ip 10.0.0.1 --client_process 4443 --time_stamp 1234567890 -q 1> temp_client1.txt 2> temp_client2.txt")
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd("LD_LIBRARY_PATH=~/data ~/data/server --interface=server%s-eth0 --unicast=10.0.%s.3 0.0.0.0 %s ~/data/server.key ~/data/server.crt -q 1> temp_server_%s_1.txt 2> temp_server_%s_2.txt &"%(str(server_id), str(server_id), str(4433+server_id), str(server_id), str(server_id)))

    time.sleep(30)

    for client_id in range(CLIENT_NUMBER):
        server_id = random.randint(0, SERVER_NUMBER - 1)
        client[client_id].cmd("LD_LIBRARY_PATH=~/data ~/data/client 10.0.%s.3 %s -i -p normal_1 -o 1 -w google.com --client_ip 10.0.0.1 --client_process %s --time_stamp 1234567890 -q 1> temp_client_%s_1.txt 2> temp_client_%s_2.txt &"%(str(server_id),str(4433+server_id),str(4433+server_id),str(client_id),str(client_id)))

 
def myNetwork():
 
    net = Mininet( topo=None,
                   build=False,
                   host=CPULimitedHost,
                   ipBase='10.0.0.0/8',
                   controller=None)
    
    ''' 
        ip地址：
            client: 10.0.0.0/16
                    10.0.x.1 clientx ip
                    10.0.x.2 clientx->switch0 网卡
            # server: 10.0.0.0/16

            switch0: 0.0.0.0
            swithc1: 0.0.0.0
        路由表（table）:
            一个client/server/router，用一张路由表
            client: 1-5
            server: 20-25
            router: 40-45
            switch0: 100
            switch1: 101
            
    '''

    print( '*** Adding controller\n' )

    print( '*** Add switches\n')
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addSwitch('switch%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone', stp=True)) ## 防止回路

    print( '*** Add hosts\n')
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('client%s'%str(client_id), cpu=0.1/CLIENT_NUMBER, ip='10.0.%s.1'%str(client_id), defaultRoute=None)) ## cpu占用为系统的10%/所有client数量
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('server%s'%str(server_id), cpu=0.3/SERVER_NUMBER, ip='10.0.%s.3'%str(server_id), defaultRoute=None))
    
    print( '*** Add links\n')
    
    for client_id in range(CLIENT_NUMBER):
        net.addLink(switch[client_id], client[client_id])
    for server_id in range(SERVER_NUMBER):
        net.addLink(switch[CLIENT_NUMBER+server_id], server[server_id])

    ## 通过多次调用addlink，使得switch之间创建多个网关的链接关系

    temp_cnt = 0
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[client_id], switch[CLIENT_NUMBER+server_id], cls=TCLink, **{'bw':100,'delay':'%sms'%str(5+temp_cnt),'loss':0}) 
        temp_cnt += 10
    
    print( '*** Starting network\n')
    net.build()

    print( '*** Starting controllers\n')
    # for controller in net.controllers:
    #     controller.start()
 
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

    ## 设置跑
    # for server_id in range(SERVER_NUMBER):
    #     server[server_id].cmd("sudo LD_LIBRARY_PATH=~/data ~/data/server --interface=ens4 --unicast=10.0.%s.3 0.0.0.0 4433 ~/data/server.key ~/data/server.crt -q &"%(str(server_id))) 

    # for client_id in range(CLIENT_NUMBER):
    #     client[client_id].cmd("sudo LD_LIBRARY_PATH=~/data ~/data/client 10.0.%s.3 4433 -i -p normal_1 -o 1 -w google.com --client_ip 10.0.%s.1 --client_process 4433 --time_stamp 1234567890 -q &"%(str(client_id), str))
    test_run(net)
    
    CLI(net)
    net.stop()
 
if __name__ == '__main__':
    setLogLevel( 'warning' )
    clear_output()
    myNetwork()
