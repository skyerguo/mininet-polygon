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
import sys
import configparser

SELECT_TOPO = copy.deepcopy(Middleware_client_dispatcher_server_large)

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
DNS_IP = "10.177.53.237"

modes = ["Polygon", "DNS", "Anycast", "FastRoute"]
if len(sys.argv) < 2:
    mode = modes[0]
    print("未输入方案，默认选择Polygon")
else:
    mode = sys.argv[1]
    if mode not in modes:
        mode = modes[0]
        print("输入方案不合法，默认选择Polygon")
# mode = modes[0]

print("mode: ", mode)

def init():
    global CLIENT_NUMBER, SERVER_NUMBER, DISPATCHER_NUMBER, SWITCH_NUMBER, SERVER_THREAD, CLIENT_THREAD, DISPATCHER_THREAD
    global bw, delay, cpu
    SERVER_NUMBER = SELECT_TOPO['server_number']
    CLIENT_NUMBER = SELECT_TOPO['client_number']
    DISPATCHER_NUMBER = SELECT_TOPO['dispatcher_number']
    SWITCH_NUMBER = SERVER_NUMBER + DISPATCHER_NUMBER + 1 + 1 # 前SN个，对应C-S，后DN个，对应C-D。导数第二个用来连DNS，最后三个用来连外网。
    SERVER_THREAD = SELECT_TOPO['server_thread']
    DISPATCHER_THREAD = SELECT_TOPO['dispatcher_thread']
    CLIENT_THREAD = SELECT_TOPO['client_thread']

    print("SWITCH_NUMBER: ", SWITCH_NUMBER)

    bw = SELECT_TOPO['bw']
    delay = SELECT_TOPO['delay']
    cpu = SELECT_TOPO['cpu']
    # zone = SELECT_TOPO['zone']

    global start_time
    start_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) 

    global virtual_machine_ip, virtual_machine_subnet, DNS_IP
    ret = subprocess.Popen("ifconfig eth0 | grep inet | awk '{print $2}' | cut -f 2 -d ':'",shell=True,stdout=subprocess.PIPE)
    virtual_machine_ip = ret.stdout.read().decode("utf-8").strip('\n')
    ret.stdout.close()
    print("virtual_machine_ip: ", virtual_machine_ip)
    virtual_machine_subnet = str(virtual_machine_ip.split('.')[0]) + '.' + \
                            str(virtual_machine_ip.split('.')[1]) + '.' + \
                            str(virtual_machine_ip.split('.')[2]) + '.0' + '/24'
    print("virtual_machine_subnet: ", virtual_machine_subnet)
    DNS_IP = virtual_machine_ip

    # 每次重新启动mongodb，以防mininet网络变化
    os.system("ps -ef | grep 'mongod' | grep -v grep | awk '{print $2}' | sudo xargs sudo kill -9")
    os.system("sudo mongod --fork --dbpath /var/lib/mongodb/ --bind_ip 127.0.0.1,%s --port 27117 --logpath=/data/mongo.log --logappend"%(virtual_machine_ip))


def clear_logs():
    os.system("sudo mn -c")
    os.system("sudo bash ../bash-scripts/kill_running.sh")


def myNetwork(net):
    ''' 
        ip地址:
            client: 10.0.0.0/16
                    10.0.x.1 clientx ip
            server: 10.0.0.0/16
                    10.0.x.3 clientx ip
            dispatcher: 10.0.0.0/16
                    10.0.x.5 dispatcherx ip
        ## 由于mininet对于interface名字不能太长，因此使用cx,sx,dx来表示clientx，serverx，dispatcherx
    '''

    ## set eth1 ifconfig 0
    os.system('ifconfig eth1 0')

    print( '*** Add switches\n')
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addSwitch('sw%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone', stp=True)) ## 防止回路

    print( '*** Add hosts\n')
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('c%s'%str(client_id), cpu=cpu['client']/CLIENT_NUMBER, ip='10.0.%s.1'%str(client_id), defaultRoute=None)) ## cpu占用为 系统的x%/所有client数量
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('s%s'%str(server_id), cpu=cpu['server']/SERVER_NUMBER, ip='10.0.%s.3'%str(server_id), defaultRoute=None))
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher.append(net.addHost('d%s'%str(dispatcher_id), cpu=cpu['dispatcher']/DISPATCHER_NUMBER, ip='10.0.%s.5'%str(dispatcher_id), defaultRoute=None)) 
    
    # dns = net.addHost("dns", ip=DNS_IP, defaultRoute=None) # 添加DNS的ip

    print( '*** Add remote controller\n')
      
    print( '*** Add links\n')
    
    ## add links among clients, servers and dispatchers
    ## C-S
    for server_id in range(SERVER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            net.addLink(switch[server_id], client[client_id], cls=TCLink, **{'bw':bw['client_server'][client_id][server_id],'delay':str(int(delay['client_server'][client_id][server_id] / 2))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
        net.addLink(switch[server_id], server[server_id])

    ## D-S
    for server_id in range(SERVER_NUMBER):
        for dispatcher_id in range(DISPATCHER_NUMBER):
            net.addLink(switch[server_id], dispatcher[dispatcher_id], cls=TCLink, **{'bw':bw['dispatcher_server'][dispatcher_id][server_id],'delay':str(int(delay['dispatcher_server'][dispatcher_id][server_id] / 2))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
        # net.addLink(switch[server_id], server[server_id]) # 都连第一个interface

    ## C-D
    for dispatcher_id in range(DISPATCHER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            net.addLink(switch[SERVER_NUMBER + dispatcher_id], client[client_id], cls=TCLink, **{'bw':bw['client_dispatcher'][client_id][dispatcher_id],'delay':str(int(delay['client_dispatcher'][client_id][dispatcher_id] / 2))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
        net.addLink(switch[SERVER_NUMBER + dispatcher_id], dispatcher[dispatcher_id])
    
    ## add links from client to DNS IP
    for client_id in range(CLIENT_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 2], client[client_id])
    
    ## add links to virtual machine ip.
    for client_id in range(CLIENT_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 1], client[client_id])

    for dispatcher_id in range(DISPATCHER_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 1], dispatcher[dispatcher_id])

    for server_id in range(SERVER_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 1], server[server_id])

    
    print( '*** Starting network\n')
    net.build()

    print( '*** Starting switches\n')

    setLogLevel( 'info' )
    print('SWITCH_NUMBER = ',SWITCH_NUMBER)
    for switch_id in range(SWITCH_NUMBER):
        net.get('sw%s'%str(switch_id)).start([])
    
    ## 定义网卡
    
    for switch_id in range(SWITCH_NUMBER):
        switch[switch_id].cmd('sysctl -w net.ipv4.ip_forward=1')
    
    ## 将最后一个switch和网卡eth1相连，并获取网关地址
    os.system("sudo ovs-vsctl add-port sw%s eth1"%str(SWITCH_NUMBER - 1))
    os.system("sudo ifconfig sw%s 10.0.100.15/24" %str(SWITCH_NUMBER - 1))

    print( '*** Post configure switches and hosts\n')
        
    ret = subprocess.Popen("ifconfig sw%s | grep inet | awk '{print $2}' | cut -f 2 -d ':'"%(str(SWITCH_NUMBER - 1)),shell=True,stdout=subprocess.PIPE)
    switch_gw = ret.stdout.read().decode("utf-8").strip('\n')
    ret.stdout.close()
    print("switch_gw: ", switch_gw)
    switch_gw_pre3 = str(switch_gw.split('.')[0]) + '.' + \
                    str(switch_gw.split('.')[1]) + '.' + \
                    str(switch_gw.split('.')[2])
    print("switch_gw_pre3: ", switch_gw_pre3)

    ## 对具体的网卡指定对应的ip
    for client_id in range(CLIENT_NUMBER):
        # for interface_id in range(1, DISPATCHER_NUMBER + SERVER_NUMBER):
        client[client_id].cmd('ifconfig c%s-eth%s 0'%(str(client_id), str(SERVER_NUMBER+DISPATCHER_NUMBER+1)))
        client[client_id].cmd('ifconfig c%s-eth%s %s.%s/24'%(str(client_id), str(SERVER_NUMBER+DISPATCHER_NUMBER+1), str(switch_gw_pre3), str(50+client_id)))
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd('ifconfig s%s-eth%s 0'%(str(server_id), str(1)))
        server[server_id].cmd('ifconfig s%s-eth%s %s.%s/24'%(str(server_id), str(1), str(switch_gw_pre3), str(100+server_id)))

    for dispatcher_id in range(DISPATCHER_NUMBER):
        for interface_id in range(SERVER_NUMBER): # 给dispatcher所有端口都绑定，保证每个端口都能转发，否则只能转发给server0
            dispatcher[dispatcher_id].cmd('ifconfig d%s-eth%s 10.0.%s.5'%(str(dispatcher_id), str(interface_id), str(dispatcher_id)))
        dispatcher[dispatcher_id].cmd('ifconfig d%s-eth%s 0'%(str(dispatcher_id), str(SERVER_NUMBER + 1)))
        dispatcher[dispatcher_id].cmd('ifconfig d%s-eth%s %s.%s/24'%(str(dispatcher_id),str(SERVER_NUMBER + 1),  str(switch_gw_pre3), str(150+dispatcher_id)))
    

    ## client,server,dispatcher发出
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            client[client_id].cmd("route add -host 10.0.%s.3 dev c%s-eth%s" %(str(server_id), str(client_id), str(server_id)))
        for dispatcher_id in range(DISPATCHER_NUMBER):
            client[client_id].cmd("route add -host 10.0.%s.5 dev c%s-eth%s" %(str(dispatcher_id), str(client_id), str(SERVER_NUMBER + dispatcher_id)))
        client[client_id].cmd("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw)))  
        # client[client_id].cmdPrint("route add -host %s dev c%s-eth%s"%(str(DNS_IP), str(client_id), str(SERVER_NUMBER + DISPATCHER_NUMBER)))

        # dns.cmdPrint("route add -host 10.0.%s.1 dev dns-eth0" % (str(client_id)))
    
    for server_id in range(SERVER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            server[server_id].cmd("route add -host 10.0.%s.1 dev s%s-eth%s" %(str(client_id), str(server_id), str(0)))
        for dispatcher_id in range(DISPATCHER_NUMBER):
            server[server_id].cmd("route add -host 10.0.%s.5 dev s%s-eth%s" %(str(dispatcher_id), str(server_id), str(0)))
        server[server_id].cmd("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw)))  

    for dispatcher_id in range(DISPATCHER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            dispatcher[dispatcher_id].cmd("route add -host 10.0.%s.1 dev d%s-eth%s" %(str(client_id), str(dispatcher_id), str(SERVER_NUMBER)))
        for server_id in range(SERVER_NUMBER):
            dispatcher[dispatcher_id].cmd("route add -host 10.0.%s.3 dev d%s-eth%s" %(str(server_id), str(dispatcher_id), str(server_id)))
        dispatcher[dispatcher_id].cmd("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw)))  
    
    # dns.cmdPrint("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw))) 
    
    ## 输出到machine_server.json
    machine_json_path = os.path.join(os.environ['HOME'], 'mininet-polygon/json-files')
    with open('{}/machine_server.json'.format(machine_json_path), 'w') as f:
        machines = {}
        for server_id in range(SERVER_NUMBER):
            server_name = 's%s'%str(server_id)
            temp_host = net.get(server_name)
            temp_ip = "10.0.%s.3"%(server_id)
            temp_ip2 = "10.0.%s.4"%(server_id)
            temp_mac = temp_host.MAC()
            machines[server_name] = {'external_ip1': temp_ip, 'external_ip2': temp_ip2,
                                     'internal_ip1': temp_ip, 'internal_ip2': temp_ip2,
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
    
    ## 输出到ip.conf
    config = configparser.ConfigParser()
    config['DNS']={}
    config['client']={}
    config['client']['ips'] = ''
    config['server']={}
    config['DNS'] = {
                'inter': '10.177.53.237',
                'exter': '10.177.53.237'
            }
    for client_id in range(CLIENT_NUMBER):
        config['client']['ips'] = config['client']['ips'] + '10.0.%s.1'%str(client_id) + ','
    config['client']['ips'] = config['client']['ips'][:-1]
    for server_id in range(SERVER_NUMBER):
        config['server']['s%s'%str(server_id)] = '10.0.%s.3'%str(server_id)
    config['layer'] = {}
    config['layer']['s0'] = 's2'
    config['layer']['s3'] = 's4'
    config['layer']['s2'] = 's1'
    config['layer']['s4'] = 's1'
    with open('../FastRoute-files/ip.conf','w') as cfg:
        config.write(cfg)

    os.system("cd ../FastRoute-files && nohup sudo python3 dns.py >/home/mininet/a.txt 2>&1 &")

def measure_start(net):
    os.system("redis-cli -a Hestia123456 -n 0 flushdb") # 清空redis的数据库，0号数据库存储测量结果

    # 设置latency的表格
    for server_id in range(SERVER_NUMBER):
        for dispatcher_id in range(DISPATCHER_NUMBER):
            os.system("redis-cli -h %s -a 'Hestia123456' set latency_s%s_d%s %s"%(str(virtual_machine_ip), str(server_id), str(dispatcher_id), str(delay['dispatcher_server'][dispatcher_id][server_id])))

    for server_id in range(SERVER_NUMBER):
        server[server_id].cmdPrint("bash ../bash-scripts/init_measurement_from_server.sh -i %s -a %s" %(str(server_id), str(start_time)))
        if mode == "FastRoute": ## 开启FastRoute的cpu监控和转移规则
            server[server_id].cmdPrint("cd ../FastRoute-files && sudo python3 LoadMonitor.py %s &"%(str(server_id)))
    
    time.sleep(10)
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmdPrint("cd ../py-scripts && bash ../bash-scripts/measurement_from_server.sh -i %s -t %s -r %s -a %s &"%(str(server_id), str(bw['dispatcher_server'][server_id]).replace(", ","+").replace("[","").replace("]",""), str(virtual_machine_ip), str(start_time)))
    
    time.sleep(10)
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher[dispatcher_id].cmdPrint("bash ../bash-scripts/measurement_record.sh -i %s -r %s -a %s &"%(str(dispatcher_id), str(virtual_machine_ip), str(start_time)))


def test_run(net):

    import random
    
    now_port = START_PORT
    for server_id in range(SERVER_NUMBER):
        server_ip = "10.0.%s.3" %(str(server_id))
        server[server_id].cmdPrint("bash ../ngtcp2-exe/start_server.sh -i %s -s %s -p %s -t %s -a %s -m %s -n %s"%(str(server_id), server_ip, str(now_port), str(SERVER_THREAD), str(start_time), mode, str(CLIENT_NUMBER + DISPATCHER_NUMBER)))
    
    # if mode == "Polygon":
    now_port = START_PORT
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher_ip = "10.0.%s.5" %(str(dispatcher_id))
        dispatcher[dispatcher_id].cmdPrint("bash ../ngtcp2-exe/start_dispatcher.sh -i %s -d %s -s %s -p %s -t %s -r %s -a %s -m %s -n %s &"%(str(dispatcher_id), dispatcher_ip, str(SERVER_NUMBER), str(now_port), str(DISPATCHER_THREAD), str(virtual_machine_ip), str(start_time), mode, str(SERVER_NUMBER + 1)))
    
    print("sleep " + str(60 + 20 * SERVER_NUMBER) + " seconds to wait servers and dispatchers start!")
    time.sleep(60 + 20 * SERVER_NUMBER)
    print("start_clients!")

    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client.sh -i %s -s %s -p %s -t %s -y %s -r %s -a %s -m %s"%(str(client_id), str(DISPATCHER_NUMBER), str(START_PORT), str(CLIENT_THREAD), str(DISPATCHER_THREAD), str(virtual_machine_ip), str(start_time), mode))
        time.sleep(3)

    
def save_config():
    config_result_path = "/data/result-logs/config/%s/"%(str(start_time))
    os.system("mkdir -p %s"%config_result_path)
    os.system("cp /data/websites/cpu/cpu/www.cpu/src/cpu.py %s"%config_result_path)
    # SELECT_TOPO
    topo_file = open(config_result_path + 'topo.json','w',encoding='utf-8')
    json.dump(SELECT_TOPO, topo_file)
    topo_file.close()


if __name__ == '__main__':
    setLogLevel( 'warning' )
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

    ## tcpdump
    # client[0].cmd("sudo tcpdump -nn -i c0-eth0 udp -w /home/mininet/test_client_sendquic_1127_c0eth0.cap &")
    # client[0].cmd("sudo tcpdump -nn -i c0-eth2 udp -w /home/mininet/test_client_sendquic_1127_c0eth2.cap &")
    # server[0].cmd("sudo tcpdump -nn -i s0-eth0 udp -w /home/mininet/test_server_sendquic_1127_s0eth0..cap &")
    # dispatcher[0].cmd("sudo tcpdump -nn -i d0-eth0 udp -w /home/mininet/test_dispatcher_sendquic_1127_d0eth0.cap &")
    # dispatcher[0].cmd("sudo tcpdump -nn -i d0-eth2 udp -w /home/mininet/test_dispatcher_sendquic_1127_d0eth2.cap &")
    
    # 测量
    print("measure_start! ")
    measure_start(net)

    # 跑实验
    test_run(net)
    save_config()

    CLI(net)
    net.stop()
