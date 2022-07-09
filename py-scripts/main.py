import sys
sys.path.append("/users/myzhou/mininet")
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
import copy
import json
import time
import os
import subprocess
import sys
import configparser

# SELECT_TOPO = copy.deepcopy(Middleware_client_dispatcher_server_large)
SELECT_TOPO = json.load(open('../json-files/topo.json', 'r'))

actual_start_time = 0

CLIENT_NUMBER = 0
DISPATCHER_NUMBER = 0
SERVER_NUMBER = 0
SWITCH_NUMBER = 0

CLIENT_THREAD = 1
DISPATCHER_THREAD = 1
SERVER_THREAD = 1

START_PORT = 14433
MAX_THROUGHPUT = 5 * 1024 ## wondershaper设置的最大带宽

switch = []
client = []
dispatcher = []
server = []

CLIENT_ZONE = []
DISPATCHER_ZONE = []
SERVER_ZONE = []
DNS_LINKS = []
DNS_OUTERS = []
bw = {}
delay = {}
cpu = {}
start_time = 0

virtual_machine_ip = "127.0.0.1"
virtual_machine_subnet = "127.0.0.1"
DNS_IP = "198.22.255.15"

zone2server_ids = []

client2latency_min_server = []

modes = ["Polygon", "Anycast", "FastRoute"]
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
    global CLIENT_ZONE, DISPATCHER_ZONE, SERVER_ZONE
    global zone2server_ids
    global DNS_LINKS, DNS_OUTERS
    global client2latency_min_server
    SERVER_NUMBER = SELECT_TOPO['server_numbezr']
    CLIENT_NUMBER = SELECT_TOPO['client_number']
    DISPATCHER_NUMBER = SELECT_TOPO['dispatcher_number']
    SWITCH_NUMBER = SERVER_NUMBER + DISPATCHER_NUMBER + 3 # 前SN个，对应C-S，后DN个，对应C-D。最后三个用来连外网。

    print('SWITCH_NUMBER = ',SWITCH_NUMBER)

    CLIENT_THREAD = SELECT_TOPO['client_thread']
    DISPATCHER_THREAD = CLIENT_NUMBER * CLIENT_THREAD
    SERVER_THREAD = CLIENT_NUMBER * CLIENT_THREAD
    # SERVER_THREAD = SELECT_TOPO['server_thread']
    # DISPATCHER_THREAD = SELECT_TOPO['dispatcher_thread']

    CLIENT_ZONE = SELECT_TOPO['client_zone']
    DISPATCHER_ZONE = SELECT_TOPO['dispatcher_zone']
    SERVER_ZONE = SELECT_TOPO['server_zone']

    bw = SELECT_TOPO['bw']
    delay = SELECT_TOPO['delay']
    cpu = SELECT_TOPO['cpu']

    DNS_LINKS = SELECT_TOPO['dns_links']
    DNS_OUTERS = SELECT_TOPO['dns_outers']

    zone2server_ids = [[] for _ in range(len(DISPATCHER_ZONE))]

    global start_time
    start_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) 

    global virtual_machine_ip, virtual_machine_subnet, DNS_IP
    ret = subprocess.Popen("ifconfig eno1 | grep inet | awk '{print $2}' | cut -f 2 -d ':'",shell=True,stdout=subprocess.PIPE)
    virtual_machine_ip = ret.stdout.read().decode("utf-8").strip('\n')
    ret.stdout.close()
    print("virtual_machine_ip: ", virtual_machine_ip)
    virtual_machine_subnet = str(virtual_machine_ip.split('.')[0]) + '.' + \
                            str(virtual_machine_ip.split('.')[1]) + '.' + \
                            str(virtual_machine_ip.split('.')[2]) + '.0' + '/24'
    print("virtual_machine_subnet: ", virtual_machine_subnet)
    DNS_IP = virtual_machine_ip

    # 每次重新启动mongodb和redis，以防mininet网络变化
    ret = subprocess.Popen("ps -ef | grep 'mongod' | grep -v grep | awk '{print $2}' | sudo xargs --no-run-if-empty kill -9",shell=True,stdout=subprocess.PIPE)     
    data=ret.communicate() #如果启用此相会阻塞主程序
    ret.wait() #等待子程序运行完毕

    ret = subprocess.Popen("sleep 3 && sudo mongod --fork --dbpath /var/lib/mongodb/ --bind_ip 127.0.0.1,%s --port 27117 --logpath=/proj/quic-PG0/data/mongo.log --logappend"%(virtual_machine_ip),shell=True,stdout=subprocess.PIPE)                   
    data=ret.communicate() #如果启用此相会阻塞主程序
    ret.wait() #等待子程序运行完毕

    ret = subprocess.Popen("sudo /usr/bin/redis-server /etc/redis/redis.conf",shell=True,stdout=subprocess.PIPE)                  
    data=ret.communicate() #如果启用此相会阻塞主程序
    ret.wait() #等待子程序运行完毕
    
    client2latency_min_server = [0 for _ in range(CLIENT_NUMBER)]
    for client_id in range(CLIENT_NUMBER):
        curr_min_latency = 1000
        curr_min_latency_server = -1
        for server_id in range(SERVER_NUMBER):
            # print(client_id, server_id)
            if float(delay['client_server'][client_id][server_id]) < curr_min_latency:
                curr_min_latency = float(delay['client_server'][client_id][server_id])
                curr_min_latency_server = server_id
        # print(client_id, curr_min_latency, curr_min_latency_server)
        client2latency_min_server[client_id] = curr_min_latency_server


    # os.system("ulimit -u 1030603") # 设置nproc即用户可以使用的进程数量


def clear_logs():
    ret = subprocess.Popen("sudo mn -c && sudo bash ../bash-scripts/kill_running.sh", shell=True, stdout=subprocess.PIPE)
    data=ret.communicate() #如果启用此相会阻塞主程序

    ret.wait() #等待子程序运行完毕


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

    ## set eno2 ifconfig 0
    os.system('ifconfig eno2 0')

    print( '*** Add switches\n')
    for switch_id in range(SWITCH_NUMBER):
        switch.append(net.addSwitch('sw%s'%str(switch_id), cls=OVSKernelSwitch, failMode='standalone', stp=True)) ## 防止回路
    
    ## 在添加后需要立刻将switch启动一次，以防超过连接数后被吞网关。
    for switch_id in range(SWITCH_NUMBER):
        net.get('sw%s'%str(switch_id)).start([])
    
    ## 定义网卡
    for switch_id in range(SWITCH_NUMBER):
        switch[switch_id].cmd('sysctl -w net.ipv4.ip_forward=1')

    ## 将最后三个switch和网卡eno2相连，并获取网关地址
    for i in range(3):
        # ret = subprocess.Popen("sudo ovs-vsctl add-port sw%s eno2 && sudo ifconfig sw%s 10.0.%s.15/24"%(str(SWITCH_NUMBER-1-i), str(SWITCH_NUMBER-1-i ), str(100+i)), shell=True,stdout=subprocess.PIPE)
        print("sudo ifconfig sw%s 10.0.%s.15/24"%(str(SWITCH_NUMBER-1-i), str(100+i)))
        ret = subprocess.Popen("sudo ifconfig sw%s 10.0.%s.15/24"%(str(SWITCH_NUMBER-1-i ), str(100+i)), shell=True,stdout=subprocess.PIPE)
        data=ret.communicate() #如果启用此相会阻塞主程序
        ret.wait() #等待子程序运行完毕

    print( '*** Post configure switches and hosts\n')

    time.sleep(5)
    
    switch_gw = [0 for _ in range(3)]
    switch_gw_pre3 = [0 for _ in range(3)]

    for i in range(3):
        ret = subprocess.Popen("ifconfig sw%s | grep inet | awk '{print $2}' | cut -f 2 -d ':'"%(str(SWITCH_NUMBER - 1 - i)),shell=True,stdout=subprocess.PIPE)
        data=ret.communicate() #如果启用此相会阻塞主程序

        ret.wait() #等待子程序运行完毕

        switch_gw[i] = data[0].decode("utf-8").strip('\n')
        print("switch_gw[i]: ", switch_gw[i])
        switch_gw_pre3[i] = str(switch_gw[i].split('.')[0]) + '.' + \
                            str(switch_gw[i].split('.')[1]) + '.' + \
                            str(switch_gw[i].split('.')[2])
        print("switch_gw_pre3[i]: ", switch_gw_pre3[i])

    print( '*** Add hosts\n')
    for client_id in range(CLIENT_NUMBER):
        client.append(net.addHost('c%s'%str(client_id), cpu=cpu['client']/CLIENT_NUMBER, ip='10.0.%s.1'%str(client_id), defaultRoute=None)) ## cpu占用为 系统的x%/所有client数量
    for server_id in range(SERVER_NUMBER):
        server.append(net.addHost('s%s'%str(server_id), cpu=cpu['server']/SERVER_NUMBER, ip='10.0.%s.3'%str(server_id), defaultRoute=None))
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher.append(net.addHost('d%s'%str(dispatcher_id), cpu=cpu['dispatcher']/DISPATCHER_NUMBER, ip='10.0.%s.5'%str(dispatcher_id), defaultRoute=None))
    
    print( '*** Add remote controller\n')
    ## 测试开始
    # s1 = net.addSwitch('s1')
    # test_host = []
    # for test_id in range(20):
    #     test_host.append(net.addHost('t%s'%str(test_id), ip='10.0.0.%s'%str(test_id+1), defaultRoute=None))
    
    # net.get('s1').start([])
    
    # s1.cmd('sysctl -w net.ipv4.ip_forward=1')

    # # print("sudo ifconfig s1 10.0.100.15/24")
    # # ret = subprocess.Popen("sudo ifconfig s1 10.0.100.15/24", shell=True,stdout=subprocess.PIPE)
    # # data=ret.communicate() #如果启用此相会阻塞主程序
    # # ret.wait() #等待子程序运行完毕

    # # ret = subprocess.Popen("ifconfig s1 | grep inet | awk '{print $2}' | cut -f 2 -d ':'",shell=True,stdout=subprocess.PIPE)
    # # data=ret.communicate() #如果启用此相会阻塞主程序
    # # ret.wait() #等待子程序运行完毕
    # # switch_gw = data[0].decode("utf-8").strip('\n')
    # # print("switch_gw: ", switch_gw)

    # for test_id in range(20):
    #     # print(test_host[test_id], s1)
    #     net.addLink(test_host[test_id], s1)

    # setLogLevel( 'info' )

    # test_host[0].cmdPrint("route add -host 10.0.0.2 dev t0-eth0")
    # test_host[1].cmdPrint("route add -host 10.0.0.1 dev t1-eth0")

    # net.build()

    # return
    ## 测试结束

    print( '*** Add links\n')
    
    ## add links among clients, servers and dispatchers
    ## bw和delay都+1，防止0的情况报错
 
    ## C-S
    for server_id in range(SERVER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            net.addLink(switch[server_id], client[client_id], cls=TCLink, **{'bw':bw['client_server'][client_id][server_id]+1,'delay':str(int(delay['client_server'][client_id][server_id] / 2 + 1))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
        net.addLink(switch[server_id], server[server_id], cls=None)
    ## D-S
    for server_id in range(SERVER_NUMBER):
        for dispatcher_id in range(DISPATCHER_NUMBER):
            net.addLink(switch[server_id], dispatcher[dispatcher_id], cls=TCLink, **{'bw':bw['dispatcher_server'][dispatcher_id][server_id]+1,'delay':str(int(delay['dispatcher_server'][dispatcher_id][server_id] / 2 + 1))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
    ## C-D
    for dispatcher_id in range(DISPATCHER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            if DISPATCHER_ZONE[dispatcher_id] == CLIENT_ZONE[client_id]: ## 减少一些用不到的边
                net.addLink(switch[SERVER_NUMBER + dispatcher_id], client[client_id], cls=TCLink, **{'bw':bw['client_dispatcher'][client_id][dispatcher_id]+1,'delay':str(int(delay['client_dispatcher'][client_id][dispatcher_id] / 2 + 1))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})
        net.addLink(switch[SERVER_NUMBER + dispatcher_id], dispatcher[dispatcher_id], cls=None)
    
    ## add links to virtual machine ip.
    for client_id in range(CLIENT_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 3], client[client_id], cls=None)

    for server_id in range(SERVER_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 2], server[server_id], cls=None)

    for dispatcher_id in range(DISPATCHER_NUMBER):
        net.addLink(switch[SWITCH_NUMBER - 1], dispatcher[dispatcher_id], cls=None)

    ## 对具体的网卡指定对应的ip
    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd('ifconfig c%s-eth%s 0'%(str(client_id), str(SERVER_NUMBER+1))) # 一个client只连一个dispatcher
        client[client_id].cmd('ifconfig c%s-eth%s %s.%s/24'%(str(client_id), str(SERVER_NUMBER+1), str(switch_gw_pre3[2]), str(100+client_id)))
    
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd('ifconfig s%s-eth%s 0'%(str(server_id), str(1)))
        server[server_id].cmd('ifconfig s%s-eth%s %s.%s/24'%(str(server_id), str(1), str(switch_gw_pre3[1]), str(150+server_id)))

    for dispatcher_id in range(DISPATCHER_NUMBER):
        for interface_id in range(SERVER_NUMBER): # 给dispatcher所有端口都绑定，保证每个端口都能转发，否则只能转发给server0
            dispatcher[dispatcher_id].cmd('ifconfig d%s-eth%s 10.0.%s.5'%(str(dispatcher_id), str(interface_id), str(dispatcher_id)))
        dispatcher[dispatcher_id].cmd('ifconfig d%s-eth%s 0'%(str(dispatcher_id), str(SERVER_NUMBER+1))) ## server个数加上和1个和client相连的sw。
        dispatcher[dispatcher_id].cmd('ifconfig d%s-eth%s %s.%s/24'%(str(dispatcher_id),str(SERVER_NUMBER+1),  str(switch_gw_pre3[0]), str(200+dispatcher_id)))
    
    ## client,server,dispatcher发出
    client_number_per_dispatcher = [0 for _ in range(DISPATCHER_NUMBER)]
    for client_id in range(CLIENT_NUMBER):
        for server_id in range(SERVER_NUMBER):
            client[client_id].cmd("route add -host 10.0.%s.3 dev c%s-eth%s" %(str(server_id), str(client_id), str(server_id)))
        cnt_dispatcher = 0
        for dispatcher_id in range(DISPATCHER_NUMBER):
            if DISPATCHER_ZONE[dispatcher_id] == CLIENT_ZONE[client_id]: ## 减少一些用不到的边
                client[client_id].cmd("route add -host 10.0.%s.5 dev c%s-eth%s" %(str(dispatcher_id), str(client_id), str(SERVER_NUMBER + cnt_dispatcher)))
                cnt_dispatcher += 1
                client_number_per_dispatcher[dispatcher_id] += 1
     
        client[client_id].cmd("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw[2])))  
    
    for server_id in range(SERVER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            server[server_id].cmd("route add -host 10.0.%s.1 dev s%s-eth%s" %(str(client_id), str(server_id), str(0)))
        for dispatcher_id in range(DISPATCHER_NUMBER):
            server[server_id].cmd("route add -host 10.0.%s.5 dev s%s-eth%s" %(str(dispatcher_id), str(server_id), str(0)))
        
        server[server_id].cmd("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw[1])))  

    for dispatcher_id in range(DISPATCHER_NUMBER):
        for client_id in range(CLIENT_NUMBER):
            if DISPATCHER_ZONE[dispatcher_id] == CLIENT_ZONE[client_id]: ## 减少一些用不到的边
                dispatcher[dispatcher_id].cmd("route add -host 10.0.%s.1 dev d%s-eth%s" %(str(client_id), str(dispatcher_id), str(SERVER_NUMBER)))
        for server_id in range(SERVER_NUMBER):
            dispatcher[dispatcher_id].cmd("route add -host 10.0.%s.3 dev d%s-eth%s" %(str(server_id), str(dispatcher_id), str(server_id)))
        
        dispatcher[dispatcher_id].cmd("route add -net %s gw %s"%(str(virtual_machine_subnet), str(switch_gw[0]))) 


    print( '*** Starting switches\n')

    # 需要加attach操作，来对switch绑定所有的eth。eth的下标从1开始
    print("client_number_per_dispatcher: ", client_number_per_dispatcher)

    for switch_id in range(SERVER_NUMBER):
        for eth_id in range(1, CLIENT_NUMBER + DISPATCHER_NUMBER + 2): # 和所有client+dispatcher相连，并连向指定server
            switch[switch_id].attach('sw%s-eth%s'%(str(switch_id), str(eth_id)))
        print("switch %s attach done"%(str(switch_id)))
        print("now_time: ", time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()))
    for switch_id in range(SERVER_NUMBER, SERVER_NUMBER + DISPATCHER_NUMBER):
        for eth_id in range(1, client_number_per_dispatcher[switch_id - SERVER_NUMBER] + 2): # 和部分client相连，并连向指定server
            switch[switch_id].attach('sw%s-eth%s'%(str(switch_id), str(eth_id)))
        print("switch %s attach done"%(str(switch_id)))
        print("now_time: ", time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()))
    for eth_id in range(1, CLIENT_NUMBER + 1): ## 和所有client相连，用来帮助client连外网
        switch[SWITCH_NUMBER - 3].attach('sw%s-eth%s'%(str(SWITCH_NUMBER - 3), str(eth_id)))
    for eth_id in range(1, SERVER_NUMBER + 1): ## 和所有server相连，用来帮助server连外网
        switch[SWITCH_NUMBER - 2].attach('sw%s-eth%s'%(str(SWITCH_NUMBER - 2), str(eth_id)))
    for eth_id in range(1, DISPATCHER_NUMBER + 1): ## 和所有dispatcher相连，用来帮助dispatcher连外网
        switch[SWITCH_NUMBER - 1].attach('sw%s-eth%s'%(str(SWITCH_NUMBER - 1), str(eth_id)))

    print( '*** Starting network\n')
    net.build()

    for client_id in range(CLIENT_NUMBER):
        client[client_id].cmd("route del -net 10.0.0.0 netmask 255.0.0.0") # 删除默认路由，防止错误路由
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmd("route del -net 10.0.0.0 netmask 255.0.0.0") # 删除默认路由，防止错误路由
    for dispatcher_id in range(DISPATCHER_NUMBER):
        dispatcher[dispatcher_id].cmd("route del -net 10.0.0.0 netmask 255.0.0.0") # 删除默认路由，防止错误路由
    
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
                                     'zone': str(SERVER_ZONE[server_id])}
            zone2server_ids[SERVER_ZONE[server_id]].append(server_id)
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
                                     'zone': str(DISPATCHER_ZONE[dispatcher_id])}
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
                                     'zone': str(CLIENT_ZONE[client_id])}
        json.dump(machines, f)
    
    # ## 输出到ip.conf
    # config = configparser.ConfigParser()
    # config['DNS']={}
    # config['client']={}
    # config['client']['ips'] = ''
    # config['server']={}
    # config['DNS'] = {
    #             'inter': '198.22.255.15',
    #             'exter': '198.22.255.15'
    #         }
    # for client_id in range(CLIENT_NUMBER):
    #     config['client']['ips'] = config['client']['ips'] + '10.0.%s.1'%str(client_id) + ','
    # config['client']['ips'] = config['client']['ips'][:-1]
    # for server_id in range(SERVER_NUMBER):
    #     config['server']['s%s'%str(server_id)] = '10.0.%s.3'%str(server_id)
    # config['layer'] = {}
    # for dns_link in DNS_LINKS:
    #     config['layer']['s%s'%str(dns_link[0])] = 's%s'%(dns_link[1])
    # with open('../FastRoute-files/ip.conf','w') as cfg:
    #     config.write(cfg)

    # os.system("cd ../FastRoute-files && nohup sudo python3 dns.py >/users/myzhou/a.txt 2>&1 &")

def measure_start(net):
    os.system("redis-cli -a Hestia123456 -n 0 flushdb") # 清空redis的数据库，0号数据库存储测量结果
    
    # ## 测试代码开始``
    # for server_id in range(SERVER_NUMBER):
    #     os.system("bash ../bash-scripts/record_cpu.sh -n %s -m s -t idle -i 1 -a %s &"%(str(server_id), str(start_time))) ## 从cgroup记录cpu的结果，因为权限问题，我们只能全局记录到文件，再由节点去访问到。
    # return
    # ## 测试代码结束

    ## 对所有server设置wondershaper，并启动ngtcp2，为了发第一次包测量实际竞争力做准备
    for server_id in range(SERVER_NUMBER):
        server[server_id].cmdPrint("bash ../bash-scripts/init_measurement_from_server.sh -i %s -m %s -a %s &" %(str(server_id), str(MAX_THROUGHPUT), str(start_time)))
        # os.system("bash ")
        if mode == "FastRoute": ## 开启FastRoute的cpu监控和转移规则
            server[server_id].cmdPrint("cd ../FastRoute-files && sudo python3 LoadMonitor.py %s &"%(str(server_id)))

    # ## 测量竞争力
    # for dispatcher_id in range(DISPATCHER_NUMBER):
    #     dispatcher[dispatcher_id].cmdPrint("bash ../bash-scripts/init_measurement_from_dispatcher.sh -i %s -n %s -a %s" %(str(dispatcher_id), str(SERVER_NUMBER), str(start_time))) ## 这里不能用&，否则会导致测量值不准

    # ## 将竞争力结果写入一个文件，方便后续使用 
    # file_size = os.path.getsize("/proj/quic-PG0/data/websites/video/downloadinginit/www.downloadinginit/cross.mp4")
    # file_size = file_size * 8 / 1024 ## 从Byte转换为Kbit的单位
    # ## 计算ngtcp2实际传输的速度
    # actual_speed = [[0 for _ in range(DISPATCHER_NUMBER)] for _ in range(SERVER_NUMBER)]
    # max_speed = 0
    # for server_id in range(SERVER_NUMBER):
    #     for dispatcher_id in range(DISPATCHER_NUMBER):
    #         f_in = open("/proj/quic-PG0/data/measurement_log/" + start_time + "/competitiveness/" + "dispatcher_" + str(dispatcher_id) + ("_server_") + str(server_id) + "_2.txt", "r")
    #         plt = 0
    #         cnt = 0
    #         for line in f_in:
    #             if "PLT" in line:
    #                 plt = plt + float(line.split(": ")[1].split(" ")[0])
    #                 cnt += 1

    #         f_in.close()

    #         while cnt != 2: # 初始测量出错了
    #             print("ERROR measurement! 重启dispatcher%s到server%s的初始传输测量"%(str(dispatcher_id), str(server_id)))
    #             dispatcher[dispatcher_id].cmdPrint("bash ../bash-scripts/redo_single_measurement_from_dispatcher.sh -i %s -s %s -a %s" %(str(dispatcher_id), str(server_id), str(start_time))) ## 重新测量dispathcer到server的空载竞争力
    #             f_in = open("/proj/quic-PG0/data/measurement_log/" + start_time + "/competitiveness/" + "dispatcher_" + str(dispatcher_id) + ("_server_") + str(server_id) + "_2.txt", "r")
    #             plt = 0
    #             cnt = 0
    #             for line in f_in:
    #                 if "PLT" in line:
    #                     plt = plt + float(line.split(": ")[1].split(" ")[0])
    #                     cnt += 1
    #             f_in.close()
    #             time.sleep(5)

           
    #         actual_speed[server_id][dispatcher_id] = file_size / (plt / 1000000) ## 单位，Kbit/s
    #         max_speed = max(max_speed, file_size / (plt / 1000000))
    # # ## 计算ngtcp2实际传输的相对竞争力，现在以实际值计算，暂时不使用
    # # relative_competitiveness = [[0 for _ in range(DISPATCHER_NUMBER)] for _ in range(SERVER_NUMBER)]
    # # for server_id in range(SERVER_NUMBER):
    # #     for dispatcher_id in range(DISPATCHER_NUMBER):
    # #         relative_competitiveness[server_id][dispatcher_id] = actual_speed[server_id][dispatcher_id] / max_speed

    # ## 写入一个文件，方便后续读取
    # competitiveness_path = "/proj/quic-PG0/data/measurement_log/" + start_time + "/competitiveness/competitiveness.txt"
    # f_out = open(competitiveness_path, "w")
    # for server_id in range(SERVER_NUMBER):
    #     for dispatcher_id in range(DISPATCHER_NUMBER):
    #         f_out.write(str(actual_speed[server_id][dispatcher_id]) + ' ')
    #     f_out.write('\n')
    # f_out.close()

    ## 删除测量带来的server进程，以免影响后续的实验结果
    os.system("ps -ef | grep '/data/server' | grep -v grep | awk '{print $2}' | xargs --no-run-if-empty sudo kill -9 > /dev/null 2>&1")
    
    ## 设置latency的表格
    for server_id in range(SERVER_NUMBER):
        for dispatcher_id in range(DISPATCHER_NUMBER):
            os.system("redis-cli -h %s -a 'Hestia123456' set latency_s%s_d%s %s"%(str(virtual_machine_ip), str(server_id), str(dispatcher_id), str(delay['dispatcher_server'][dispatcher_id][server_id])))

    ## 在client端启动nload    
    for client_id in range(CLIENT_NUMBER): 
        client[client_id].cmdPrint("bash ../bash-scripts/init_measurement_from_client.sh -i %s -a %s -z %s -n %s"%(str(client_id), str(start_time), str(CLIENT_ZONE[client_id]), str(SERVER_NUMBER)))
    time.sleep(10)
    
    for server_id in range(SERVER_NUMBER):
        os.system("bash ../bash-scripts/record_cpu.sh -n %s -m s -t idle -i 1 -a %s &"%(str(server_id), str(start_time))) ## 从cgroup记录cpu的结果，因为权限问题，我们只能全局记录到文件，再由节点去访问到。
        temp_bw = []
        for dispatcher_id in range(DISPATCHER_NUMBER):
            temp_bw.append(bw['dispatcher_server'][dispatcher_id][server_id])
        server[server_id].cmdPrint("cd ../py-scripts && bash ../bash-scripts/measurement_from_server.sh -i %s -t %s -r %s -a %s -m %s &"%(str(server_id), str(temp_bw).replace(", ","+").replace("[","").replace("]",""), str(virtual_machine_ip), str(start_time), str(MAX_THROUGHPUT)))
    
    # 这一块用来周期性记录redis实验数据的，暂时先不启动，会带来一定的overhead
    # time.sleep(10)
    # for dispatcher_id in range(DISPATCHER_NUMBER):
    #     dispatcher[dispatcher_id].cmdPrint("bash ../bash-scripts/measurement_record.sh -i %s -r %s -a %s &"%(str(dispatcher_id), str(virtual_machine_ip), str(start_time)))


def run(net):

    import random
    
    for server_id in range(SERVER_NUMBER):
        server_ip = "10.0.%s.3" %(str(server_id))
        server[server_id].cmdPrint("bash ../ngtcp2-exe/start_server.sh -i %s -s %s -p %s -t %s -a %s -m %s -n %s"%(str(server_id), server_ip, str(START_PORT), str(SERVER_THREAD), str(start_time), mode, str(CLIENT_NUMBER + DISPATCHER_NUMBER)))
        time.sleep(SERVER_THREAD / 80) # 必须要有较长sleep，不然太多进程同时产生，直接GG
    
    # if mode == "Polygon":
    for dispatcher_id in range(DISPATCHER_NUMBER):
        now_port = START_PORT
        for client_id in range(CLIENT_NUMBER): 
            if CLIENT_ZONE[client_id] == DISPATCHER_ZONE[dispatcher_id]: ## 只在需要的端口开dispatcher
                dispatcher[dispatcher_id].cmdPrint("bash ../ngtcp2-exe/start_dispatcher.sh -i %s -s %s -p %s -t %s -r %s -a %s -m %s -n %s -z %s &"%(str(dispatcher_id), str(SERVER_NUMBER), str(now_port), str(CLIENT_THREAD), str(virtual_machine_ip), str(start_time), mode, str(SERVER_NUMBER+1), DISPATCHER_ZONE[dispatcher_id]))
                time.sleep(1)
            now_port += CLIENT_THREAD
        time.sleep(5)
    
    print("sleep " + str(60 + 5 * (SERVER_NUMBER + DISPATCHER_NUMBER)) + " seconds to wait servers and dispatchers start!")
    time.sleep(60 + 5 * (SERVER_NUMBER + DISPATCHER_NUMBER))
    
    global actual_start_time
    actual_start_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    print("actual_start_time: ", actual_start_time)
    print("start_clients!")

    now_port = START_PORT
    for client_id in range(CLIENT_NUMBER):
        # client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client_timeline.sh -i %s -p %s -t %s -r %s -a %s -m %s -z %s -d %s -o %s"%(str(client_id), str(now_port), str(CLIENT_THREAD), str(virtual_machine_ip), str(start_time), mode, str(CLIENT_ZONE[client_id]), str(random.choice(zone2server_ids[CLIENT_ZONE[client_id]])), str(random.choice(DNS_OUTERS[CLIENT_ZONE[client_id]])))) ## 给Anycast随机同一个zone里的server

        # client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client_timeline.sh -i %s -p %s -t %s -r %s -a %s -m %s -z %s -d %s -o %s"%(str(client_id), str(now_port), str(CLIENT_THREAD), str(virtual_machine_ip), str(start_time), mode, str(CLIENT_ZONE[client_id]), str(client2latency_min_server[client_id]), str(random.choice(DNS_OUTERS[CLIENT_ZONE[client_id]])))) ## 给Anycast随机同一个latency最小的server


        # client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client_timeline.sh -i %s -p %s -t %s -r %s -a %s -m %s -z %s -d %s -o %s -c 1"%(str(client_id), str(now_port), str(CLIENT_THREAD), str(virtual_machine_ip), str(start_time), mode, str(CLIENT_ZONE[client_id]), str(client2latency_min_server[client_id]), str(random.choice(DNS_OUTERS[CLIENT_ZONE[client_id]])))) ## 使用cpu，按照trace执行cpu
        # client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client.sh -i %s -p %s -t %s -r %s -a %s -m %s -z %s -d %s -o %s"%(str(client_id), str(now_port), str(CLIENT_THREAD), str(virtual_machine_ip), str(start_time), mode, str(CLIENT_ZONE[client_id]), str(client2latency_min_server[client_id]), str(random.choice(DNS_OUTERS[CLIENT_ZONE[client_id]])))) ## 没有cpu，顺序执行bw和latency，Anycast选最小
        # client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client.sh -i %s -p %s -t %s -r %s -a %s -m %s -z %s -d %s -o %s"%(str(client_id), str(now_port), str(CLIENT_THREAD), str(virtual_machine_ip), str(start_time), mode, str(CLIENT_ZONE[client_id]), str(random.choice(zone2server_ids[CLIENT_ZONE[client_id]])), str(random.choice(DNS_OUTERS[CLIENT_ZONE[client_id]])))) ## 没有cpu，顺序执行bw和latency，Anycast随机
        client[client_id].cmdPrint("bash ../ngtcp2-exe/start_client.sh -i %s -p %s -t %s -r %s -a %s -m %s -z %s -d %s -o %s"%(str(client_id), str(now_port), str(CLIENT_THREAD), str(virtual_machine_ip), str(start_time), mode, str(CLIENT_ZONE[client_id]), str(client2latency_min_server[client_id]), str(random.choice(DNS_OUTERS[CLIENT_ZONE[client_id]])))) ## 有cpu，4：4：1，Anycast选最小

        now_port += CLIENT_THREAD
        time.sleep(3)

    
def save_config():
    config_result_path ="/proj/quic-PG0/data/result-logs/config/%s/"%(str(start_time))
    os.system("mkdir -p %s"%config_result_path)
    os.system("cp /proj/quic-PG0/data/websites/cpu/cpu/www.cpu/src/cpu.py %s"%config_result_path)

    # SELECT_TOPO
    topo_file = open(config_result_path + 'topo.json', 'w', encoding='utf-8')
    SELECT_TOPO['mode'] = mode
    json.dump(SELECT_TOPO, topo_file)
    topo_file.close()
    
    print(actual_start_time, file=open(config_result_path + "actual_start_time.txt", "w"))

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
    setLogLevel( 'info' )
    
    ## 测量
    print("measure_start! ")
    measure_start(net)

    ## 跑实验
    run(net)
    save_config()

    CLI(net)
    net.stop()
