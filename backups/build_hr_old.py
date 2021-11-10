from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import json
import os

init_json_path = os.environ['HOME'] + '/polygon/DNS_CDN'
machine_json_path = os.environ['HOME']

def sendAndWait(host, line, send=True, debug=True):
    if not send:
        return ''
    print('*** Executing cmd:', line)
    host.sendCmd(line)
    ret = host.waitOutput().strip()
    if ret != '' and debug:
        print(ret)
    return ret

def runCmd(host, lines):
    lines = iter(lines)
    for line in lines:
        line = line.strip()
        if line.lower().startswith('if'):
            line += ' echo 1;else echo 0;fi'
            vsend = int(sendAndWait(host, line, debug=False))
            line = next(lines, None).strip()
            while line and not line.lower().startswith('fi'):
                sendAndWait(host, line, vsend)
                line = next(lines, None).strip()
        elif line != '':
            sendAndWait(host, line)

class MyTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        with open('{}/machine_server.json'.format(init_json_path), 'r') as f:
            servers = json.load(f)
            for name in servers.keys():
                if 'internal_ip1' in servers[name]:
                    host = self.addHost(name)
                    self.addLink(host, switch)
        with open('{}/machine_client.json'.format(init_json_path), 'r') as f:
            clients = json.load(f)
            for i in range(len(clients)):
                host = self.addHost('cl%s'%(i+1))
                self.addLink(host, switch)

if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=MyTopo())
    net.addNAT().configDefault()
    net.start()
    
    h = net.hosts[0]
    sendAndWait(h, 'echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null')
    with open('./envir.sh', 'r') as script:
        lines = script.readlines()
        runCmd(h, lines)

    with open('{}/machine_server.json'.format(init_json_path), 'r') as f:
        servers = json.load(f)
        for sv in servers.keys():
            if 'internal_ip1' in servers[sv]:
                host = net.get(sv)
                servers[sv]['internal_ip1'] = servers[sv]['internal_ip2'] = host.IP()
                servers[sv]['mac1'] = servers[sv]['mac2'] = host.MAC()
    with open('{}/machine_server.json'.format(init_json_path), 'w') as f:
        json.dump(servers, f)

    with open('{}/machine_client.json'.format(init_json_path), 'r') as f:
        clients = json.load(f)
        for i in range(len(clients)):
            host = net.get('cl%s'%(i+1))
            clients[i]['hostname'] = host.IP()
    with open('{}/machine_client.json'.format(init_json_path), 'w') as f:
        json.dump(clients, f)
    
    with open('{}/machine.json'.format(machine_json_path), 'r') as f:
        servers = json.load(f)
        for sv in servers.keys():
            if sv.endswith('sv'):
                host = net.get(sv)
                sendAndWait(host, "bash ./setup_server.sh")
            elif sv.endswith('rt'):
                host = net.get(sv)
                sendAndWait(host, "bash ./setup_router.sh")

    CLI(net)
    net.stop()
