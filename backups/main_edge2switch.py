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
import time
import os
import subprocess

SELECT_TOPO = copy.deepcopy(Middleware_client_dispatcher_server_test)

CLIENT_NUMBER = 0
DISPATCHER_NUMBER = 0
SERVER_NUMBER = 0
SWITCH_NUMBER = 0

CLIENT_THREAD = 1
DISPATCHER_THREAD = 1
SERVER_THREAD = 1

START_PORT = 4433

switch = []
client = []
dispatcher = []
server = []
bw = {}
delay = {}
cpu = {}
# zone = {}
start_time = 0

virtual_machine_ip = "127.0.0.1"
virtual_machine_subnet = "127.0.0.1"

modes = ["Polygon", "DNS", "Anycast", "FastRoute"]
mode = modes[1]

def init():
    global CLIENT_NUMBER, SERVER_NUMBER, DISPATCHER_NUMBER, SWITCH_NUMBER, SERVER_THREAD, CLIENT_THREAD, DISPATCHER_THREAD
    global bw, delay, cpu
    SERVER_NUMBER = SELECT_TOPO['server_number']
    CLIENT_NUMBER = SELECT_TOPO['client_number']
    DISPATCHER_NUMBER = SELECT_TOPO['dispatcher_number']
    SWITCH_NUMBER = SERVER_NUMBER * CLIENT_NUMBER + CLIENT_NUMBER * DISPATCHER_NUMBER + SERVER_NUMBER * DISPATCHER_NUMBER+ 1 # 最后一位用来连外网
    SERVER_THREAD = SELECT_TOPO['server_thread']
    DISPATCHER_THREAD = SELECT_TOPO['dispatcher_thread']
    CLIENT_THREAD = SELECT_TOPO['client_thread']

    bw = SELECT_TOPO['bw']
    delay = SELECT_TOPO['delay']
    cpu = SELECT_TOPO['cpu']
    # zone = SELECT_TOPO['zone']

    global start_time
    start_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) 

    global virtual_machine_ip, virtual_machine_subnet
    ret = subprocess.Popen("ifconfig eth0 | grep inet | awk '{print $2}' | cut -f 2 -d ':'",shell=True,stdout=subprocess.PIPE)
    virtual_machine_ip = ret.stdout.read().decode("utf-8").strip('\n')
    ret.stdout.close()
    print("virtual_machine_ip: ", virtual_machine_ip)
    virtual_machine_subnet = str(virtual_machine_ip.split('.')[0]) + '.' + \
                            str(virtual_machine_ip.split('.')[1]) + '.' + \
                            str(virtual_machine_ip.split('.')[2]) + '.0' + '/24'

    print("virtual_machine_subnet: ", virtual_machine_subnet)

    # 每次重新启动mongodb，以防mininet网络变化
    os.system("ps -ef | grep 'mongod' | grep -v grep | awk '{print $2}' | sudo xargs sudo kill -9")
    os.system("sudo mongod --fork --dbpath /var/lib/mongodb/ --bind_ip 127.0.0.1,%s --port 27117 --logpath=/data/mongo.log --logappend"%(virtual_machine_ip))


def clear_logs():
    # os.system("rm -f temp_*")
    # os.system("sudo bash ../bash-scripts/clear_logs.sh")
    os.system("sudo bash ../bash-scripts/kill_running.sh")


def myNetwork(net):
    ''' 
        ip地址：
            client: 10.0.0.0/16
                    10.0.x.1 clientx ip
                    10.0.x.1 clientx->switch0 网卡
            server: 10.0.0.0/16
                    10.0.x.3 clientx ip
                    10.0.x.3 clientx->switch0 网卡
            dispatcher: 10.0.0.0/16
                    10.0.x.5 dispatcherx ip
                    10.0.x.5 dispatcherx->switch0 网卡
                    10.0.x.7 dispatcherx->switch1 网卡
        ## 由于mininet对于interface名字不能太长，因此使用cx,sx,dx来表示client，server，dispatcher
    '''

    ## set eth1 ifconfig 0
    os.system('ifconfig eth1 0')

    print( '*** Add switches\n')
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addSwitch('switch%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone', stp=True)) ## 防止回路

    print( '*** Add hosts\n')
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('c%s'%str(client_id), cpu=cpu['client']/CLIENT_NUMBER, ip='10.0.%s.1'%str(client_id), defaultRoute=None)) ## cpu占用为 系统的x%/所有client数量
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('s%s'%str(server_id), cpu=cpu['server']/SERVER_NUMBER, ip='10.0.%s.3'%str(server_id), defaultRoute=None))
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher.append(net.addHost('d%s'%str(dispatcher_id), cpu=cpu['dispatcher']/DISPATCHER_NUMBER, ip='10.0.%s.5'%str(dispatcher_id), defaultRoute=None)) 

    print( '*** Add remote controller\n')
      
    print( '*** Add links\n')
    
    ## add links among clients, servers and dispatchers
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[client_id * CLIENT_NUMBER + server_id], client[client_id], cls=TCLink, **{'bw':bw['client_server'][client_id][server_id],'delay':str(int(delay['client_server'][client_id][server_id] / 2))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
            net.addLink(switch[client_id * CLIENT_NUMBER + server_id], server[server_id])

        for dispatcher_id in range(DISPATCHER_NUMBER):
            net.addLink(switch[CLIENT_NUMBER * SERVER_NUMBER + client_id * CLIENT_NUMBER + dispatcher_id], client[client_id], cls=TCLink, **{'bw':bw['client_dispatcher'][client_id][dispatcher_id],'delay':str(int(delay['client_dispatcher'][client_id][dispatcher_id] / 2))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
            net.addLink(switch[CLIENT_NUMBER * SERVER_NUMBER + client_id * CLIENT_NUMBER + dispatcher_id], dispatcher[dispatcher_id])

    for dispatcher_id in range(DISPATCHER_NUMBER):
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[CLIENT_NUMBER * SERVER_NUMBER + CLIENT_NUMBER * DISPATCHER_NUMBER + dispatcher_id * DISPATCHER_NUMBER + server_id], dispatcher[dispatcher_id], cls=TCLink, **{'bw':bw['dispatcher_server'][dispatcher_id][server_id],'delay':str(int(delay['dispatcher_server'][dispatcher_id][server_id] / 2))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
            net.addLink(switch[CLIENT_NUMBER * SERVER_NUMBER + CLIENT_NUMBER * DISPATCHER_NUMBER + dispatcher_id * DISPATCHER_NUMBER + server_id], server[server_id])
        # net.addLink(switch[SWITCH_NUMBER - 1], server[server_id])
    
    ## add links from dispatchers and servers to virtual machine ip.
    for dispatcher_id in range(DISPATCHER_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 1], dispatcher[dispatcher_id])

    for server_id in range(SERVER_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 1], server[server_id])

    ## 通过多次调用addlink，使得switch之间创建多个网关的链接关系
    
    print( '*** Starting network\n')
    net.build()

    # print( '*** Starting controllers\n')
    # for controller in net.controllers:
    #     print("controller: ", controller)
    #     controller.start()
 
    print( '*** Starting switches\n')
    for switch_id in range(SWITCH_NUMBER):
        net.get('switch%s'%str(switch_id)).start([])
    
    ## 定义网卡
    
    for switch_id in range(SWITCH_NUMBER):
        switch[switch_id].cmd('sysctl -w net.ipv4.ip_forward=1')
    
    ## 将最后一个switch和网卡eth1相连，并获取网关地址
    os.system("sudo ovs-vsctl add-port switch%s eth1"%str(SWITCH_NUMBER - 1))
    
    ## 别用了，傻逼dhclient
    # os.system("sudo dhclient -r switch%s" %str(SWITCH_NUMBER - 1))
    # os.system("sudo dhclient switch%s" %str(SWITCH_NUMBER - 1))

    os.system("sudo ifconfig switch%s 10.0.100.15/24" %str(SWITCH_NUMBER - 1))

    print( '*** Post configure switches and hosts\n')
        
    ret = subprocess.Popen("ifconfig switch%s | grep inet | awk '{print $2}' | cut -f 2 -d ':'"%(str(SWITCH_NUMBER - 1)),shell=True,stdout=subprocess.PIPE)
    switch_gw = ret.stdout.read().decode("utf-8").strip('\n')
    ret.stdout.close()
    print("switch_gw: ", switch_gw)
    switch_gw_pre3 = str(switch_gw.split('.')[0]) + '.' + \
                    str(switch_gw.split('.')[1]) + '.' + \
                    str(switch_gw.split('.')[2])
    print("switch_gw_pre3: ", switch_gw_pre3)

    ## 对具体的网卡指定对应的ip
    for client_id in range(CLIENT_NUMBER):
        for interface_id in range(DISPATCHER_NUMBER + SERVER_NUMBER):
            client[client_id].cmdPrint('ifconfig c%s-eth%s 10.0.%s.1'%(str(client_id), str(interface_id), str(client_id)))
    
    for server_id in range(SERVER_NUMBER):
        for interface_id in range(DISPATCHER_NUMBER + CLIENT_NUMBER):
            server[server_id].cmdPrint('ifconfig s%s-eth%s 10.0.%s.3'%(str(server_id), str(interface_id), str(server_id)))
        server[server_id].cmdPrint('ifconfig s%s-eth%s 0'%(str(server_id), str(CLIENT_NUMBER + DISPATCHER_NUMBER)))
        server[server_id].cmdPrint('ifconfig s%s-eth%s %s.%s/24'%(str(server_id), str(CLIENT_NUMBER + DISPATCHER_NUMBER), str(switch_gw_pre3), str(50+server_id)))

    for dispatcher_id in range(DISPATCHER_NUMBER):
        for interface_id in range(SERVER_NUMBER + CLIENT_NUMBER):
            dispatcher[dispatcher_id].cmdPrint('ifconfig d%s-eth%s 10.0.%s.5'%(str(dispatcher_id), str(interface_id), str(dispatcher_id)))
        dispatcher[dispatcher_id].cmdPrint('ifconfig d%s-eth%s 0'%(str(dispatcher_id), str(CLIENT_NUMBER + DISPATCHER_NUMBER)))
        dispatcher[dispatcher_id].cmdPrint('ifconfig d%s-eth%s %s.%s/24'%(str(dispatcher_id),str(CLIENT_NUMBER + DISPATCHER_NUMBER),  str(switch_gw_pre3), str(100+dispatcher_id)))

    ## client,server,dispatcher发出
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            client[client_id].cmdPrint("route add -host 10.0.%s.3 dev c%s-eth%s" % (str(server_id), str(client_id), str(server_id)))
        for dispatcher_id in range(DISPATCHER_NUMBER):
            client[client_id].cmdPrint("route add -host 10.0.%s.5 dev c%s-eth%s" % (str(dispatcher_id), str(client_id), str(SERVER_NUMBER + dispatcher_id)))
    
    for server_id in range(SERVER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            server[server_id].cmdPrint("route add -host 10.0.%s.1 dev s%s-eth%s" % (str(client_id), str(server_id), str(client_id)))
        for dispatcher_id in range(DISPATCHER_NUMBER):
            server[server_id].cmdPrint("route add -host 10.0.%s.5 dev s%s-eth%s" % (str(dispatcher_id), str(server_id), str(CLIENT_NUMBER + dispatcher_id)))
        server[server_id].cmdPrint("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw)))  

    for dispatcher_id in range(DISPATCHER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            dispatcher[dispatcher_id].cmdPrint("route add -host 10.0.%s.1 dev d%s-eth%s" % (str(client_id), str(dispatcher_id), str(client_id)))
        for server_id in range(SERVER_NUMBER):
            dispatcher[dispatcher_id].cmdPrint("route add -host 10.0.%s.3 dev d%s-eth%s" % (str(server_id), str(dispatcher_id), str(CLIENT_NUMBER + server_id)))
        dispatcher[dispatcher_id].cmdPrint("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw)))  
    
    ## 输出到machine_server.json
    machine_json_path = os.path.join(os.environ['HOME'], 'mininet-polygon/json-files')
    with open('{}/machine_server.json'.format(machine_json_path), 'w') as f:
        machines = {}
        for server_id in range(SERVER_NUMBER):
            server_name = 's%s'%str(server_id)
            temp_host = net.get(server_name)
            temp_ip = "10.0.%s.3"%(server_id)
            temp_mac = temp_host.MAC()
            machines[server_name] = {'external_ip1': temp_ip, 'external_ip2': temp_ip,
                                     'internal_ip1': temp_ip, 'internal_ip2': temp_ip,
                                     'mac1': temp_mac, 'mac2': temp_mac,
                                     'zone': str(server_id)}
        json.dump(machines, f)
    
    ## 输出到machine_dispatcher.json
    with open('{}/machine_dispatcher.json'.format(machine_json_path), 'w') as f:
        machines = {}
        for dispatcher_id in range(DISPATCHER_NUMBER):
            dispatcher_name = 'd%s'%str(dispatcher_id)
            temp_host = net.get(dispatcher_name)
            temp_ip = "10.0.%s.5"%(dispatcher_id)
            temp_mac = temp_host.MAC()
            machines[dispatcher_name] = {'external_ip1': temp_ip, 'external_ip2': temp_ip,
                                     'internal_ip1': temp_ip, 'internal_ip2': temp_ip,
                                     'mac1': temp_mac, 'mac2': temp_mac,
                                     'zone': str(dispatcher_id)}
        json.dump(machines, f)
    
    ## 输出到machine_client.json
    with open('{}/machine_client.json'.format(machine_json_path), 'w') as f:
        machines = {}
        for client_id in range(CLIENT_NUMBER):
            client_name = 'c%s'%str(client_id)
            temp_host = net.get(client_name)
            temp_ip = "10.0.%s.1"%(client_id)
            temp_mac = temp_host.MAC()
            machines[client_name] = {'external_ip1': temp_ip, 'external_ip2': temp_ip,
                                     'internal_ip1': temp_ip, 'internal_ip2': temp_ip,
                                     'mac1': temp_mac, 'mac2': temp_mac,
                                     'zone': str(client_id)}
        json.dump(machines, f)

def measure_start(net):
    os.system("redis-cli -a Hestia123456 -n 0 flushdb") # 清空redis的数据库，0号数据库存储测量结果
    # os.system("redis-cli -a Hestia123456 -n 1 flushdb") # 清空redis的数据库，1号数据库存储Polygon的PLT结果

    # 设置latency的表格
    for server_id in range(SERVER_NUMBER):
        for dispatcher_id in range(DISPATCHER_NUMBER):
            os.system("redis-cli -h %s -a 'Hestia123456' set latency_s%s_d%s %s"%(str(virtual_machine_ip), str(server_id), str(dispatcher_id), str(delay['dispatcher_server'][dispatcher_id][server_id])))

    for server_id in range(SERVER_NUMBER):
        server[server_id].cmdPrint("bash ../bash-scripts/init_measurement_from_server.sh -i %s -a %s" %(str(server_id), str(start_time)))
    
    time.sleep(5)
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmdPrint("bash ../bash-scripts/measurement_from_server.sh -i %s -t %s -r %s -a %s &"%(str(server_id), str(bw['dispatcher_server'][server_id]).replace(", ","+").replace("[","").replace("]",""), str(virtual_machine_ip), str(start_time)))
    
    time.sleep(5)
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher[dispatcher_id].cmdPrint("bash ../bash-scripts/measurement_record.sh -i %s -r %s -a %s &"%(str(dispatcher_id), str(virtual_machine_ip), str(start_time)))


def test_run(net):

    import random
    
    now_port = START_PORT
    for server_id in range(SERVER_NUMBER):
        server_ip = "10.0.%s.3" %(str(server_id))
        server[server_id].cmdPrint("bash ../ngtcp2-exe/start_server.sh -i %s -s %s -p %s -t %s -a %s -m %s -n %s"%(str(server_id), server_ip, str(now_port), str(SERVER_THREAD), str(start_time), mode, str(CLIENT_NUMBER + DISPATCHER_NUMBER)))
    
    if mode == "Polygon":
        now_port = START_PORT
        for dispatcher_id in range(DISPATCHER_NUMBER):
            dispatcher_ip = "10.0.%s.5" %(str(dispatcher_id))
            dispatcher[dispatcher_id].cmdPrint("bash ../ngtcp2-exe/start_dispatcher.sh -i %s -s %s -p %s -t %s -r %s -a %s -m %s &"%(str(dispatcher_id), dispatcher_ip, str(now_port), str(DISPATCHER_THREAD), str(virtual_machine_ip), str(start_time), mode))

    print("sleep " + str(60 + 20 * SERVER_NUMBER) + " seconds to wait servers and dispatchers start!")
    time.sleep(60 + 20 * SERVER_NUMBER)
    print("start_clients!")

    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client.sh -i %s -s %s -p %s -t %s -y %s -r %s -a %s -m %s"%(str(client_id), str(DISPATCHER_NUMBER), str(START_PORT), str(CLIENT_THREAD), str(DISPATCHER_THREAD), str(virtual_machine_ip), str(start_time), mode))
        time.sleep(3)


if __name__ == '__main__':
    setLogLevel( 'info' )
    clear_logs()

    init()

    net = Mininet( topo=None,
                build=False,
                host=CPULimitedHost,
                ipBase='10.0.0.0/8',
                controller=None,
                waitConnected=True)

    myNetwork(net)
    
    ## 等待网络构建好
    print("sleep 30 seconds to wait mininet construction! ")
    time.sleep(30)

    # 测试网络连接
    # for client_id in range(CLIENT_NUMBER):
        # for dispatcher_id in range(DISPATCHER_NUMBER):
            # client[client_id].cmdPrint("ping -i.2 -c5 d%s"%(dispatcher_id))

    ## 用socket，直接从dispatcher发送给server，不走gre了
    ## 测量
    print("measure_start! ")
    measure_start(net)

    ## tcpdump
    # client[0].cmd("sudo tcpdump -enn 'host 10.0.0.1' -w /home/mininet/test_client_sendquic_newipudp.cap &")
    # server[0].cmd("sudo tcpdump -enn 'host 10.0.0.3' -w /home/mininet/test_server_sendquic_newipudp.cap &")
    # dispatcher[0].cmd("sudo tcpdump -i any -enn -w /home/mininet/test_dispatcher_sendquic_d0all.cap &")
    # dispatcher[0].cmd("sudo tcpdump -enn 'host 10.0.0.5' -w /home/mininet/test_dispatcher_sendquic_newipudp.cap &")
    
    ## 跑实验
    test_run(net)

    CLI(net)
    net.stop()