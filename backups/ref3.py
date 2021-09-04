from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController,CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections

class MyTopo(Topo):

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)
        L1=2
        L2=L1*2
        L3=L2
        Core_Switches=[]
        Aggregation_Switches=[]
        Edge_Switches=[]

        # add swithes
        for i in range(L1):
            sw=self.addSwitch('C{}'.format(i+1))
            Core_Switches.append(sw)

        for i in range(L2):
            sw=self.addSwitch('A{}'.format(i+1))
            Aggregation_Switches.append(sw)

        for i in range(L3):
            sw=self.addSwitch('E{}'.format(i+1))
            Edge_Switches.append(sw)
        
        # add links
        for sw1 in Core_Switches:
            for sw2 in Aggregation_Switches:
                self.addLink(sw1,sw2)

        for i in range(0,L2,2):
            for sw1 in Aggregation_Switches[i:i+2]:
                for sw2 in Edge_Switches[i:i+2]:
                    self.addLink(sw1,sw2)
        
        # add hosts and links
        count=1
        for sw1 in Edge_Switches:
            for i in range(2):
                host=self.addHost('H{}'.format(count))
                self.addLink(sw1,host)
                count+=1

topos={'mytopo':(lambda:MyTopo())}
