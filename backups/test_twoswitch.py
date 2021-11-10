from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
 
def myNetwork():
 
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')
    
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

    CLIENT_NUMBER = 1
    SWITCH_NUMBER = 2
    SERVER_NUMBER = 1
    ROUTER_NUMBER = 0

    info( '*** Adding controller\n' )

    info( '*** Add switches\n')
    switch = []
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addSwitch('switch%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone', stp=True))

    info( '*** Add hosts\n')
    client = []
    server = []
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('client%s'%str(client_id), cls=CPULimitedHost, ip='10.0.%s.1'%str(client_id), defaultRoute=None))
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('server%s'%str(server_id), cls=CPULimitedHost, ip='10.0.%s.3'%str(server_id), defaultRoute=None))
    
    info( '*** Add links\n')
    
    for switch_id in range(SWITCH_NUMBER-1):
        for client_id in range(CLIENT_NUMBER):
            net.addLink(switch[switch_id], client[client_id])
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[switch_id], server[server_id])

    ## 通过多次调用addlink，使得switch之间创建多个网关的链接关系

    temp_cnt = 0
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[0], switch[1], cls=TCLink, **{'bw':100,'delay':'%sms'%str(5+temp_cnt)}) 
            temp_cnt += 10
    
    info( '*** Starting network\n')
    net.build()

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
 
    info( '*** Starting switches\n')
    net.get('switch0').start([])
    net.get('switch1').start([])
    ## 定义网卡
    
    # for switch_id in range(SWITCH_NUMBER):
    #     switch[switch_id].cmd('sysctl -w net.ipv4.ip_forward=1')
   
    info( '*** Post configure switches and hosts\n')
    ## 对具体的网卡指定对应的ip
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd('ifconfig client%s-eth0 10.0.%s.1'%(str(client_id), str(client_id)))
        client[client_id].cmd('ifconfig client%s-eth1 10.0.%s.2'%(str(client_id), str(client_id)))
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd('ifconfig server%s-eth0 10.0.%s.3'%(str(server_id), str(server_id)))
        server[server_id].cmd('ifconfig server%s-eth1 10.0.%s.4'%(str(server_id), str(server_id)))

    for client_id in range(CLIENT_NUMBER):
        switch[0].cmd('ifconfig switch0-eth%s 10.0.0.%s'%(str(client_id+1), str(50+client_id*2)))
        switch[1].cmd('ifconfig switch1-eth%s 10.0.0.%s'%(str(client_id+1), str(50+client_id*2+1)))

    for server_id in range(SERVER_NUMBER):
        switch[0].cmd('ifconfig switch0-eth%s 10.0.0.%s'%(str(CLIENT_NUMBER+server_id+1), str(50+(CLIENT_NUMBER+server_id)*2)))
        switch[1].cmd('ifconfig switch1-eth%s 10.0.0.%s'%(str(CLIENT_NUMBER+server_id+1), str(50+(CLIENT_NUMBER+server_id)*2+1)))

    now_index = 0
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            switch[0].cmd('ifconfig switch0-eth%s 10.0.0.%s'%(str(CLIENT_NUMBER+SERVER_NUMBER+1+int(now_index/2)), str(100+now_index)))
            switch[1].cmd('ifconfig switch1-eth%s 10.0.0.%s'%(str(CLIENT_NUMBER+SERVER_NUMBER+1+int(now_index/2)), str(100+now_index+1)))
            now_index += 2

    ## 删除旧的路由表
    ## 删除client路由表
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd("ip route del 10.0.0.0/8 dev client%s-eth0 proto kernel scope link src 10.0.%s.1"%(str(client_id), str(client_id)))
        client[client_id].cmd("ip route del 10.0.0.0/8 dev client%s-eth1 proto kernel scope link src 10.0.%s.2"%(str(client_id), str(client_id)))

    ## 删除server路由表
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd("ip route del 10.0.0.0/8 dev server%s-eth0 proto kernel scope link src 10.0.%s.3"%(str(server_id), str(server_id)))
        server[server_id].cmd("ip route del 10.0.0.0/8 dev server%s-eth1 proto kernel scope link src 10.0.%s.4"%(str(server_id), str(server_id)))

    ## 删除switch路由表
    for client_id in range(CLIENT_NUMBER):
        switch[0].cmd("ip route del 10.0.0.0/8 dev switch0-eth%s proto kernel scope link src 10.0.0.%s"%(str(client_id+1), str(50+client_id*2)))
        switch[1].cmd("ip route del 10.0.0.0/8 dev switch1-eth%s proto kernel scope link src 10.0.0.%s"%(str(client_id+1), str(50+client_id*2+1)))

    for server_id in range(SERVER_NUMBER):
        switch[0].cmd("ip route del 10.0.0.0/8 dev switch0-eth%s proto kernel scope link src 10.0.0.%s"%(str(CLIENT_NUMBER+server_id+1), str(50+(CLIENT_NUMBER+server_id)*2)))
        switch[1].cmd("ip route del 10.0.0.0/8 dev switch1-eth%s proto kernel scope link src 10.0.0.%s"%(str(CLIENT_NUMBER+server_id+1), str(50+(CLIENT_NUMBER+server_id)*2+1)))
    
    now_index = 0
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            switch[0].cmd('ip route del 10.0.0.0/8 dev switch0-eth%s proto kernel scope link src 10.0.0.%s'%(str(CLIENT_NUMBER+SERVER_NUMBER+1+int(now_index/2)), str(100+now_index)))
            switch[1].cmd('ip route del 10.0.0.0/8 dev switch1-eth%s proto kernel scope link src 10.0.0.%s'%(str(CLIENT_NUMBER+SERVER_NUMBER+1+int(now_index/2)), str(100+now_index+1)))
            now_index += 2

    ## client,server发出
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd("ip route add default dev client%s-eth0 proto kernel scope link"%(str(client_id)))  
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd("ip route add default dev server%s-eth0 proto kernel scope link"%(str(server_id)))  
    
    ## switch0根据包来的地址，决定路由表的使用
    for client_id in range(CLIENT_NUMBER):
        switch[0].cmd("ip rule add from 10.0.%s.1 table %s"%(str(client_id), str(1+client_id)))
    
    for server_id in range(SERVER_NUMBER):
        switch[0].cmd("ip rule add from 10.0.%s.3 table %s"%(str(server_id), str(21+server_id)))
    
    ## switch0的路由表配置
    now_index = 0
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            switch[0].cmd("ip route add 10.0.%s.3 dev switch0-eth%s proto kernel scope link table %s"%(str(server_id), str(CLIENT_NUMBER+SERVER_NUMBER+1+now_index), str(1+client_id)))
            switch[0].cmd("ip route add 10.0.%s.1 dev switch0-eth%s proto kernel scope link table %s"%(str(client_id), str(CLIENT_NUMBER+SERVER_NUMBER+1+now_index), str(21+server_id)))

            now_index += 1
    
    ## switch1到client,server
    for client_id in range(CLIENT_NUMBER):
        switch[1].cmd("ip route add 10.0.%s.1 dev switch1-eth%s proto kernel scope link"%(str(client_id), str(client_id+1)))

    for server_id in range(SERVER_NUMBER):
        switch[1].cmd("ip route add 10.0.%s.3 dev switch1-eth%s proto kernel scope link"%(str(server_id), str(CLIENT_NUMBER+server_id+1)))    
    

    CLI(net)
    net.stop()
 
if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
