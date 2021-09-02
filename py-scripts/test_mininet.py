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
        switch.append(net.addSwitch('switch%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone'))

    info( '*** Add hosts\n')
    client = []
    server = []
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('client%s'%str(client_id), cls=CPULimitedHost, ip='10.0.%s.1'%str(client_id), defaultRoute=None))
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('server%s'%str(server_id), cls=CPULimitedHost, ip='10.0.%s.3'%str(client_id), defaultRoute=None))
    
    info( '*** Add links\n')
    
    for switch_id in range(SWITCH_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            net.addLink(switch[switch_id], client[client_id])
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[switch_id], server[server_id])

    ## 通过多次调用addlink，使得switch之间创建多个网关的链接关系
    s0s1 = {'bw':100,'delay':'5ms'}
    net.addLink(switch[0], switch[1], cls=TCLink, **s0s1) 
    
    info( '*** Starting network\n')
    net.build()

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
 
    info( '*** Starting switches\n')
    net.get('switch0').start([])
    net.get('switch1').start([])
    ## 定义网卡
    
    for switch_id in range(SWITCH_NUMBER):
        switch[switch_id].cmd('sysctl -w net.ipv4.ip_forward=1')
   
    info( '*** Post configure switches and hosts\n')
    ## 对具体的网卡指定对应的ip
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd('ifconfig client%s-eth0 10.0.%s.1'%(str(client_id), str(client_id)))
        client[client_id].cmd('ifconfig client%s-eth1 10.0.%s.2'%(str(client_id), str(client_id)))
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd('ifconfig server%s-eth0 10.0.%s.3'%(str(server_id), str(server_id)))
        server[server_id].cmd('ifconfig server%s-eth1 10.0.%s.4'%(str(server_id), str(server_id)))

    for client_id in range(CLIENT_NUMBER):
        switch[0].cmd('ifconfig switch0-eth%s 10.0.0.%s'%(str(client_id), str(50+client_id*2)))
        switch[1].cmd('ifconfig switch1-eth%s 10.0.0.%s'%(str(client_id), str(50+client_id*2+1)))

    for server_id in range(SERVER_NUMBER):
        switch[0].cmd('ifconfig switch0-eth%s 10.0.0.%s'%(str(CLIENT_NUMBER+server_id), str(50+(CLIENT_NUMBER+server_id)*2)))
        switch[1].cmd('ifconfig switch1-eth%s 10.0.0.%s'%(str(CLIENT_NUMBER+server_id), str(50+(CLIENT_NUMBER+server_id)*2+1)))

    switch[0].cmd('ifconfig switch0-eth2 10.0.0.100') 
    switch[1].cmd('ifconfig switch1-eth2 10.0.0.101')   

    ## 删除旧的路由表
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd("ip route del 10.0.0.0/8 dev client%s-eth0 proto kernel scope link src 10.0.0.1"%(str(client_id)))
        client[client_id].cmd("ip route del 10.0.0.0/8 dev client%s-eth1 proto kernel scope link src 10.0.0.2"%(str(client_id)))

    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd("ip route del 10.0.0.0/8 dev server%s-eth0 proto kernel scope link src 10.0.0.3"%(str(client_id)))
        server[server_id].cmd("ip route del 10.0.0.0/8 dev server%s-eth1 proto kernel scope link src 10.0.0.4"%(str(client_id)))

    switch[0].cmd("ip route del 10.0.0.0/8 dev switch0-eth0 proto kernel scope link src 10.0.0.50")
    switch[0].cmd("ip route del 10.0.0.0/8 dev switch0-eth1 proto kernel scope link src 10.0.0.52")
    switch[0].cmd("ip route del 10.0.0.0/8 dev switch0-eth2 proto kernel scope link src 10.0.0.100")

    switch[1].cmd("ip route del 10.0.0.0/8 dev switch1-eth0 proto kernel scope link src 10.0.0.51")
    switch[1].cmd("ip route del 10.0.0.0/8 dev switch1-eth1 proto kernel scope link src 10.0.0.53")
    switch[1].cmd("ip route del 10.0.0.0/8 dev switch1-eth2 proto kernel scope link src 10.0.0.101") 

    # ## 添加规则，从哪个ip来的，使用哪个路由表
    # for client_id in range(CLIENT_NUMBER):
        # client[client_id].cmd("ip rule add from 10.0.%s.1 table %s"%(str(client_id), str(client_id+1)))
        # switch[0].cmd("ip rule add from 10.0.%s.1 table %s"%(str(client_id), str(100+client_id)))
        # switch[1].cmd("ip rule add from 10.0.%s.2 table %s"%(str(client_id), str(100+client_id)))
        # client[client_id].cmd("ip rule add from 10.0.%s.2 table %s"%(str(client_id), str(client_id+1)))
 
    # for server_id in range(SERVER_NUMBER):
    #     server[server_id].cmd("ip rule add from 10.0.%s.3 table %s"%(str(server_id), str(server_id+21)))
    #     switch[0].cmd("ip rule add from 10.0.%s.3 table %s"%(str(server_id), str(100+CLIENT_NUMBER+server_id)))
    #     switch[1].cmd("ip rule add from 10.0.%s.4 table %s"%(str(server_id), str(100+CLIENT_NUMBER+server_id)))
    #     # server[server_id].cmd("ip rule add from 10.0.%s.4 table %s"%(str(server_id), str(server_id+21)))

    
    client[0].cmd("ip route add 10.0.0.3 dev client0-eth0 proto kernel scope link")
    client[0].cmd("ip route add default dev client0-eth0 proto kernel scope link")

    switch[0].cmd("ip rule add from 10.0.0.1 table 1")
    switch[0].cmd("ip rule add from 10.0.0.3 table 2")
    switch[0].cmd("ip route add 10.0.0.3 dev switch0-eth2 proto kernel scope link table 1")
    switch[0].cmd("ip route add 10.0.0.1 dev switch0-eth2 proto kernel scope link table 2")

    switch[1].cmd("ip route add 10.0.0.1 dev switch1-eth0 proto kernel scope link")
    switch[1].cmd("ip route add 10.0.0.3 dev switch1-eth1 proto kernel scope link")

    server[0].cmd("ip route add 10.0.0.1 dev server0-eth0 proto kernel scope link")
    server[0].cmd("ip route add default dev server0-eth0 proto kernel scope link")

    ## 添加节点上的路由下一跳规则，以及具体的每个路由表的操作
    # for client_id in range(CLIENT_NUMBER):
    #     ## 添加规则，目的地址为xxx, dev表示用哪个网口，via表示下一跳的地址，scope表示适用范围
    #     client[client_id].cmd("ip route add 10.0.%s.0/24 dev client%s-eth0 scope link table %s"%(str(client_id), str(client_id), str(client_id+1)))
    #     ## 并填入这个路由表的默认路由（其他情况的发包逻辑）
    #     client[client_id].cmd("ip route add default via 10.0.%s.%s dev client%s-eth0 table %s"%(str(client_id), str(50+client_id*2), str(client_id), str(client_id+1))) ## 可以去掉via？
    #     client[client_id].cmd("ip route add default scope global nexthop via 10.0.%s.%s dev client%s-eth0"%(str(client_id), str(50+client_id*2), str(client_id))) ## 可以把scope改为link？


 
    CLI(net)
    net.stop()
 
if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
