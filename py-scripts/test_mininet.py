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
 
    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    switch0 = net.addHost('switch0', cls=Node, ip='0.0.0.0')
    # s1 = net.addHost('s1', cls=Node, ip='0.0.0.0')
    # s2 = net.addHost('s2', cls=Node, ip='0.0.0.0')
    # s3 = net.addHost('s3', cls=Node, ip='0.0.0.0')
    info( '*** Add hosts\n')
    client = []
    for i in range(2):
        client.append(net.addHost('client%s'%str(i), cls=Host, ip='10.0.%s.2/24'%str(i), defaultRoute=None))
    
    info( '*** Add links\n')
    # net.addLink(client[0], s1)
    # net.addLink(client[0], s3)
    # net.addLink(s1, s2)
    # net.addLink(s2, client[1])
    # net.addLink(s3, s2)
    for i in range(2):
        net.addLink(switch0, client[i])
    
    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
 
    info( '*** Starting switches\n')
    ## 定义网卡
    client[0].cmd('ifconfig client0-eth0 0')
    client[0].cmd('ifconfig client0-eth1 0')
    client[1].cmd('ifconfig client1-eth0 0')
    switch0.cmd('ifconfig switch0-eth0 0')
    switch0.cmd('ifconfig switch0-eth1 0')
    switch0.cmd('sysctl -w net.ipv4.ip_forward=1')
    # s1.cmd('ifconfig s1-eth0 0')
    # s1.cmd('ifconfig s1-eth1 0')
    # s2.cmd('ifconfig s2-eth0 0')
    # s2.cmd('ifconfig s2-eth1 0')
    # s2.cmd('ifconfig s2-eth2 0')
    # s3.cmd('ifconfig s3-eth0 0')
    # s3.cmd('ifconfig s3-eth1 0')
    # s1.cmd('sysctl -w net.ipv4.ip_forward=1')
    # s2.cmd('sysctl -w net.ipv4.ip_forward=1')
    # s3.cmd('sysctl -w net.ipv4.ip_forward=1')
    info( '*** Post configure switches and hosts\n')
    client[0].cmd('ifconfig client0-eth0 10.0.0.2/24')
    # client[0].cmd('ifconfig client0-eth1 10.0.2.2/24')
    client[1].cmd('ifconfig client1-eth0 10.0.1.2/24')
    
    switch0.cmd('ifconfig switch0-eth0 172.16.0.1/24')
    switch0.cmd('ifconfig switch0-eth1 172.16.1.1/24')
    # s1.cmd('ifconfig s1-eth1 172.16.2.1/24')
    # s2.cmd('ifconfig s2-eth0 172.16.2.2/24')
    # s2.cmd('ifconfig s2-eth1 10.0.1.1/24')
    # s2.cmd('ifconfig s2-eth2 192.168.2.2/24')
    # s3.cmd('ifconfig s3-eth0 10.0.2.1/24')
    # s3.cmd('ifconfig s3-eth1 192.168.2.1/24')
 
    # s1.cmd('route add -net 10.0.1.0/24 gw 172.16.2.2')
    # s2.cmd('route add -net 10.0.0.0/24 gw 172.16.2.1')
    # s2.cmd('route add -net 10.0.2.0/24 gw 192.168.2.1') 
    # s3.cmd('route add -net 10.0.1.0/24 gw 192.168.2.2')

    ## 添加到网络的路由，gw表示是哪个网关
    switch0.cmd('route add -net 10.0.0.0/24 gw 172.16.0.1')
    switch0.cmd('route add -net 10.0.1.0/24 gw 172.16.1.1')

    ## 添加规则，从哪个ip来的，使用哪个路由表
    client[0].cmd("ip rule add from 10.0.0.2 table 1")
    # client[0].cmd("ip rule add from 10.0.2.2 table 2")
    client[1].cmd("ip rule add from 10.0.1.2 table 1")

    ## 添加规则，dev表示用哪个网口，scope表示适用范围，并填入这个路由表的默认路由
    client[0].cmd("ip route add 10.0.0.0/24 dev client0-eth0 scope link table 1")
    client[0].cmd("ip route add default via 10.0.0.1 dev client0-eth0 table 1")

    # client[0].cmd("ip route add 10.0.2.0/24 dev client0-eth1 scope link table 2")
    # client[0].cmd("ip route add default via 10.0.2.1 dev client0-eth1 table 2")
    
    client[1].cmd("ip route add 10.0.1.0/24 dev client1-eth0 scope link table 1")
    client[1].cmd("ip route add default via 10.0.1.1 dev client1-eth0 table 1")

    ## 添加hop的关系
    client[0].cmd("ip route add default scope global nexthop via 10.0.0.1 dev client0-eth0") 
    client[1].cmd("ip route add default scope global nexthop via 10.0.1.1 dev client1-eth0")
 
    CLI(net)
    net.stop()
 
if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
