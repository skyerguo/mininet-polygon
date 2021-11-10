from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import json
import os

root_path = os.environ['HOME'] + '/mininet-polygon/'
json_path = root_path + 'json-files/'
bash_path = root_path + 'bash-scripts/'

# class setGre():
#     def setEthernet():
#         h1 =  network.get('h1')
#         server.setIP('10.0.0.10', intf='h1-eth1')
#         server.setMAC('00:00:00:00:00:10', intf='h1-eth1')
    

#     def main(self):
#         self.setEthernet()


def sendAndWait(host, line, send=True, debug=True):
    if not send:
        return ''
    print('*** Executing cmd:', line)
    # 通过设置环境变量对bash需要的参数进行赋值
    # temp_command = "echo export mininet_host_name=%s >> ~/.bashrc" % host
    # os.system(temp_command)
    # temp_command = "echo export mininet_host_name=%s >> ~/.zshrc" % host
    # os.system(temp_command)

    host.sendCmd(line)
    ret = host.waitOutput().strip()
    if ret != '' and debug:
        print(ret)
    return ret

class MyTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        segment_id = 0
        with open('{}/machine_server.json'.format(json_path), 'r') as f:
            servers = json.load(f)
            for name in servers.keys():
                if 'internal_ip1' in servers[name]:
                    # host = self.addHost(name)
                    host = self.addHost(name, ip='10.0.%s.2/24' % str(segment_id))
                    segment_id += 1
                    self.addLink(host, switch)
        with open('{}/machine_client.json'.format(json_path), 'r') as f:
            clients = json.load(f)
            for i in range(len(clients)):
                # host = self.addHost('cl%s'%(i+1))
                host = self.addHost('cl%s'%(i+1), ip='10.0.%s.2/24' % str(segment_id))
                segment_id += 1
                self.addLink(host, switch)

if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=MyTopo())
    net.addNAT().configDefault()
    net.start()
    
    h = net.hosts[0]

    with open('{}/machine_server.json'.format(json_path), 'r') as f:
        servers = json.load(f)
        for sv in servers.keys():
            if 'internal_ip1' in servers[sv]:
                host = net.get(sv)
                servers[sv]['internal_ip1'] = servers[sv]['internal_ip2'] = host.IP()
                servers[sv]['mac1'] = servers[sv]['mac2'] = host.MAC()
    # print(servers)
    with open('{}/machine_server.json'.format(json_path), 'w') as f:
        json.dump(servers, f)

    with open('{}/machine_client.json'.format(json_path), 'r') as f:
        clients = json.load(f)
        for i in range(len(clients)):
            host = net.get('cl%s'%(i+1))
            clients[i]['hostname'] = host.IP()
    # print(clients)
    with open('{}/machine_client.json'.format(json_path), 'w') as f:
        json.dump(clients, f)
    
    # with open('{}/machine.json'.format(json_path), 'r') as f:
    #     servers = json.load(f)
    #     for sv in servers.keys():
    #         if sv.endswith('sv'):
    #             host = net.get(sv)
    #             sendAndWait(host, "bash %sgre_setup_server.sh" % bash_path)
    #             break
    #         elif sv.endswith('rt'):
    #             host = net.get(sv)
    #             sendAndWait(host, "bash %s ./gre_setup_router.sh" % bash_path)

    ## 必须先server后router，server有删除旧的路由表的操作
    # os.system("bash %sgre_setup_server_all.sh" % bash_path)
    # print("gre_setup_server done!")
    # os.system("bash %sgre_setup_router_all.sh" % bash_path)
    # print("gre_setup_router done!")
    
    # sh_host = net.get("s1")
    # sh_host.sendAndWait("bash %sgre_setup_server_all.sh" % bash_path)
    # sh_host.sendAndWait("bash %sgre_setup_router_all.sh" % bash_path)

    CLI(net)
    net.stop()
