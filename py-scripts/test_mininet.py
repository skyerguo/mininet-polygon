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
            client: 1-5
            switch0: 100
            switch1: 101
            
    '''

    CLIENT_NUMBER = 2
    SWITCH_NUMBER = 2
    SERVER_NUMBER = 2
    ROUTER_NUMBER = 2

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    switch = []
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addHost('switch%s'%str(switch_id), cls=Node, ip='0.0.0.0'))

    info( '*** Add hosts\n')
    client = []
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('client%s'%str(client_id), cls=Host, ip='10.0.%s.1/24'%str(client_id), defaultRoute=None))
    
    info( '*** Add links\n')
    for switch_id in range(SWITCH_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            net.addLink(switch[switch_id], client[client_id])
    
    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
 
    info( '*** Starting switches\n')
    ## 定义网卡
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd('ifconfig client%s-eth0 0'%str(client_id))

    for switch_id in range(SWITCH_NUMBER):
        switch[switch_id].cmd('sysctl -w net.ipv4.ip_forward=1')
        for client_id in range(CLIENT_NUMBER):
            switch[switch_id].cmd('ifconfig switch%s-eth%s 0'%(str(switch_id), str(client_id)))
   
    info( '*** Post configure switches and hosts\n')
    ## 对具体的网卡指定对应的ip
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd('ifconfig client%s-eth0 10.0.%s.1/24'%(str(client_id), str(client_id)))
    
    for switch_id in range(SWITCH_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            switch[switch_id].cmd('ifconfig switch%s-eth%s 10.0.%s.2/24'%(str(switch_id), str(client_id), str(client_id)))


    ## 对具体的单节点网卡之间通信的测试 
    switch[0].cmd('route add -net 10.0.0.2 gw 10.0.1.2')

    ## 添加规则，从哪个ip来的，使用哪个路由表
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd("ip rule add from 10.0.%s.1 table %s"%(str(client_id), str(client_id+1)))
    
    for switch_id in range(SWITCH_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            switch[switch_id].cmd("ip rule add from 10.0.%s.2 table %s"%(str(client_id), str(switch_id+100)))

    ## 添加节点上的路由下一跳规则，以及具体的每个路由表的操作
    for client_id in range(CLIENT_NUMBER):
        ## 添加规则，目的地址为xxx, dev表示用哪个网口，via表示下一跳的地址，scope表示适用范围
        client[client_id].cmd("ip route add 10.0.%s.0/24 dev client%s-eth0 scope link table %s"%(str(client_id), str(client_id), str(client_id+1)))
        ## 并填入这个路由表的默认路由（其他情况的发包逻辑）
        client[client_id].cmd("ip route add default via 10.0.%s.2 dev client%s-eth0 table %s"%(str(client_id), str(client_id), str(client_id+1))) ## 可以去掉via？
        client[client_id].cmd("ip route add default scope global nexthop via 10.0.%s.2 dev client%s-eth0"%(str(client_id), str(client_id))) ## 可以把scope改为link？
 
    CLI(net)
    net.stop()
 
if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
