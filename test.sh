sudo mn --topo=single,2
sh ifconfig eth1 0
sh sudo ifconfig s1 up
sh sudo ovs-vsctl add-port s1 eth1
sh dhclient s1
h1 ifconfig h1-eth0 0
h1 dhclient h1-eth0
h1 route add -net 10.177.53.0/24 gw 10.0.2.15 ## 后面这个是s1的ifconfig 10.0.2.15
h1 ping 10.177.53.165
