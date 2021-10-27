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

SELECT_TOPO = copy.deepcopy(test_1_1_1)

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
zone = {}

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
    global CLIENT_NUMBER, SERVER_NUMBER, DISPATCHER_NUMBER, SWITCH_NUMBER, SERVER_THREAD, CLIENT_THREAD
    global bw, delay, cpu
    SERVER_NUMBER = SELECT_TOPO['server_number']
    CLIENT_NUMBER = SELECT_TOPO['client_number']
    DISPATCHER_NUMBER = SELECT_TOPO['dispatcher_number']
    SWITCH_NUMBER = SERVER_NUMBER + CLIENT_NUMBER + DISPATCHER_NUMBER * 2 
    SERVER_THREAD = SELECT_TOPO['server_thread']
    DISPATCHER_THREAD = SELECT_TOPO['dispatcher_thread']
    CLIENT_THREAD = SELECT_TOPO['client_thread']

    bw = SELECT_TOPO['bw']
    delay = SELECT_TOPO['delay']
    cpu = SELECT_TOPO['cpu']
    zone = SELECT_TOPO['zone']


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


    print( '*** Add switches\n')
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addSwitch('switch%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone', stp=True)) ## 防止回路

    print( '*** Add hosts\n')
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('c%s'%str(client_id), cpu=cpu['client']/CLIENT_NUMBER, ip='10.0.%s.1'%str(client_id), defaultRoute=None)) ## cpu占用为 系统的x%/所有client数量
        # client.append(net.addHost('client%s'%str(client_id), ip='10.0.%s.1'%str(client_id), defaultRoute=None))
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('s%s'%str(server_id), cpu=cpu['server']/SERVER_NUMBER, ip='10.0.%s.3'%str(server_id), defaultRoute=None))
        # server.append(net.addHost('server%s'%str(server_id), ip='10.0.%s.3'%str(server_id), defaultRoute=None))
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher.append(net.addHost('d%s'%str(dispatcher_id), cpu=cpu['dispatcher']/DISPATCHER_NUMBER, ip='10.0.%s.5'%str(dispatcher_id), defaultRoute=None)) 
      
    print( '*** Add links\n')
    
    for client_id in range(CLIENT_NUMBER):
        net.addLink(switch[client_id], client[client_id])
    for server_id in range(SERVER_NUMBER):
        net.addLink(switch[CLIENT_NUMBER+server_id], server[server_id])
    for dispatcher_id in range(DISPATCHER_NUMBER):
        net.addLink(switch[CLIENT_NUMBER+SERVER_NUMBER+dispatcher_id], dispatcher[dispatcher_id])
    for dispatcher_id in range(DISPATCHER_NUMBER):
        net.addLink(switch[CLIENT_NUMBER+SERVER_NUMBER+DISPATCHER_NUMBER+dispatcher_id], dispatcher[dispatcher_id])

    ## 通过多次调用addlink，使得switch之间创建多个网关的链接关系

    ## client_server
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[client_id], switch[CLIENT_NUMBER+server_id], cls=TCLink, **{'bw':bw['client_server'][client_id][server_id],'delay':str(delay['client_server'][client_id][server_id])+'ms'}) 
    
    ## client_dispatcher
    for client_id in range(CLIENT_NUMBER):
        for dispatcher_id in range(DISPATCHER_NUMBER):
            net.addLink(switch[client_id], switch[CLIENT_NUMBER+SERVER_NUMBER+dispatcher_id], cls=TCLink, **{'bw':bw['client_dispatcher'][client_id][dispatcher_id],'delay':str(delay['client_dispatcher'][client_id][dispatcher_id])+'ms'}) 
    
    ## dispatcher_server
    for dispatcher_id in range(DISPATCHER_NUMBER):
        for server_id in range(SERVER_NUMBER):
            net.addLink(switch[CLIENT_NUMBER+SERVER_NUMBER+dispatcher_id], switch[CLIENT_NUMBER+server_id], cls=TCLink, **{'bw':bw['dispatcher_server'][dispatcher_id][server_id],'delay':str(delay['dispatcher_server'][dispatcher_id][server_id])+'ms'})
    
    ## dispatcher_dispatcher
    for dispatcher_id_0 in range(DISPATCHER_NUMBER):
        for dispatcher_id_1 in range(dispatcher_id_0 + 1, DISPATCHER_NUMBER):
            net.addLink(switch[CLIENT_NUMBER+SERVER_NUMBER+DISPATCHER_NUMBER+dispatcher_id_0], switch[CLIENT_NUMBER+SERVER_NUMBER+DISPATCHER_NUMBER+dispatcher_id_1], cls=TCLink, **{'bw':bw['dispatcher_dispatcher'][dispatcher_id_0][dispatcher_id_1],'delay':str(delay['dispatcher_dispatcher'][dispatcher_id_0][dispatcher_id_1])+'ms'}) 
    
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
        client[client_id].cmd('ifconfig c%s-eth0 10.0.%s.1'%(str(client_id), str(client_id)))
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd('ifconfig s%s-eth0 10.0.%s.3'%(str(server_id), str(server_id)))

    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher[dispatcher_id].cmd('ifconfig d%s-eth0 10.0.%s.5'%(str(dispatcher_id), str(dispatcher_id)))

    ## client,server,dispatcher发出
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd("ip route add default dev c%s-eth0 proto kernel scope link"%(str(client_id)))  
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd("ip route add default dev s%s-eth0 proto kernel scope link"%(str(server_id))) 

    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher[dispatcher_id].cmd("ip route add default dev d%s-eth0 proto kernel scope link"%(str(dispatcher_id)))  
    
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


def gre_setup(net):
    for dispatcher_id in range(DISPATCHER_NUMBER):
        print("bash ../bash-scripts/gre_setup_dispatcher_single.sh -i %s"%(str(dispatcher_id)))
        dispatcher[dispatcher_id].cmd("bash ../bash-scripts/gre_setup_dispatcher_single.sh -i %s"%(str(dispatcher_id)))

def measure_start(net):
    for server_id in range(1):
        print("bash ../bash-scripts/init_measurement_from_server.sh -i %s"%(str(server_id)))
        server[server_id].cmd("bash ../bash-scripts/init_measurement_from_server.sh -i %s" %(str(server_id)))
    
    time.sleep(5)
    
    for server_id in range(1):
        print("bash ../bash-scripts/measurement_from_server.sh -i %s -t %s"%(str(server_id), str(SELECT_TOPO['bw']['dispatcher_server'][0]).replace(", ","+").replace("[","").replace("]","")))
        server[server_id].cmd("bash ../bash-scripts/measurement_from_server.sh -i %s -t %s"%(str(server_id), str(SELECT_TOPO['bw']['dispatcher_server'][0]).replace(", ","+").replace("[","").replace("]","")))


def test_run(net):

    import random
    
    now_port = START_PORT
    start_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) 
    for server_id in range(SERVER_NUMBER):
        server_ip = "10.0.%s.3" %(str(server_id))
        print("bash ../ngtcp2-exe/start_server.sh -i %s -s %s -p %s -t %s -a %s"%(str(server_id), server_ip, str(now_port), str(SERVER_THREAD), str(start_time)))
        server[server_id].cmd("bash ../ngtcp2-exe/start_server.sh -i %s -s %s -p %s -t %s -a %s"%(str(server_id), server_ip, str(now_port), str(SERVER_THREAD), str(start_time)))
        now_port += SERVER_THREAD
    
    now_port = START_PORT
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher_ip = "10.0.%s.5" %(str(dispatcher_id))
        print("bash ../ngtcp2-exe/start_dispatcher.sh -i %s -s %s -p %s -t %s -a %s"%(str(dispatcher_id), dispatcher_ip, str(now_port), str(DISPATCHER_THREAD), str(start_time)))
        dispatcher[dispatcher_id].cmd("bash ../ngtcp2-exe/start_dispatcher.sh -i %s -s %s -p %s -t %s -a %s"%(str(dispatcher_id), dispatcher_ip, str(now_port), str(DISPATCHER_THREAD), str(start_time)))
        now_port += SERVER_THREAD

    time.sleep(30 + 5 * SERVER_NUMBER)

    for client_id in range(CLIENT_NUMBER):
        print("bash ../ngtcp2-exe/start_client.sh -i %s -s %s -p %s -t %s -y %s -a %s"%(str(client_id), str(DISPATCHER_NUMBER), str(START_PORT), str(CLIENT_THREAD), str(DISPATCHER_THREAD), str(start_time)))
        client[client_id].cmd("bash ../ngtcp2-exe/start_client.sh -i %s -s %s -p %s -t %s -y %s -a %s"%(str(client_id), str(DISPATCHER_NUMBER), str(START_PORT), str(CLIENT_THREAD), str(DISPATCHER_THREAD), str(start_time)))
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
    ## 设置跑
    time.sleep(20) ## 等待网络构建好
    # gre_setup(net)
    ## 用socket，直接从dispatcher发送给server，不走gre了
    # measure_start(net)
    # test_run(net)
    CLI(net)
    net.stop()
