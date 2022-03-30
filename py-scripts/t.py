from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        Switch = self.addSwitch( 's0' )
        leftHost = self.addHost( 'h0' )
        self.addLink( leftHost, Switch )
        for i in range(60):
            rightHost = self.addHost( 'h'+str(i+1) )

            # Add links
            self.addLink( Switch, rightHost )


topos = { 'mytopo': ( lambda: MyTopo() ) }
