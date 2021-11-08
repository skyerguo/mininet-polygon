from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import Intf
from mininet.log import setLogLevel, info

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        '*** Add switches\n'
        s1 = self.addSwitch('s1')
        info("**type s1 --> ", type(s1), "\n")

        s2 = self.addSwitch('s2')

        '*** Add hosts\n'
        h2 = self.addHost('h2')
        # Add links
        '*** Add links\n'
        self.addLink(h2, s2)

def addIface(mn):
    s1_node = mn.getNodeByName("s1")
    Intf("eth1", node=s1_node)
    CLI(mn)

tests = { 'addIf': addIface }
topos = { 'mytopo': ( lambda: MyTopo() ) }