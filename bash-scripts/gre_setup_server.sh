cd ${HOME}
date > gre.sh.start_ts

sudo iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP
for bridge in `sudo ovs-vsctl show| grep Bridge| sed -E 's/ +Bridge //'| sed -E 's/"//g'`
do
    sudo ovs-vsctl del-br $bridge
done

hostname=$(ifconfig | head -1 | cut -d'-' -f1)
export router=${hostname:0:`expr ${#hostname} - 2`}rt
router_primary_ip_inner=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["router"]]["internal_ip1"])'`
router_secondary_ip_inner=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["router"]]["internal_ip2"])'`
router_bridge_name=router
router_port_name=tunnel-router
router_ip=$router_primary_ip_inner
router_anycast_ip=$router_secondary_ip_inner
sudo ovs-vsctl add-br $router_bridge_name

sudo ovs-vsctl add-port $router_bridge_name $router_port_name -- set interface $router_port_name type=vxlan, options:remote_ip=$router_ip
router_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $router_port_name| tail -n1| egrep -o "[0-9]+"`
sudo ifconfig $router_bridge_name $router_anycast_ip/32 up
var=`ifconfig ${router_bridge_name}| grep ether`
vars=( $var )
router_mac=${vars[1]}
sudo ovs-ofctl del-flows $router_bridge_name
sudo ovs-ofctl add-flow $router_bridge_name in_port=$router_port,actions=mod_dl_dst:${router_mac},mod_nw_dst:${router_anycast_ip},local
sudo ovs-ofctl add-flow $router_bridge_name in_port=local,actions=$router_port
sudo arp -s $router_primary_ip_inner 00:00:00:00:00:00 -i $router_bridge_name
sudo ip route flush table 2 > /dev/null 2>&1
sudo ip rule delete table 2 > /dev/null 2>&1
sudo ip route add default via $router_anycast_ip dev $router_bridge_name tab 2 > /dev/null 2>&1
sudo ip rule add from $router_anycast_ip/32 tab 2 priority 600 > /dev/null 2>&1

date > gre.sh.end_ts