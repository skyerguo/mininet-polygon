cd ${HOME}
date > gre.sh.start_ts

export hostname=$(ifconfig | head -1 | cut -d'-' -f1)
iface_secondary=${hostname}'-eth0'
var=$(ifconfig ${iface_secondary}|grep ether); vars=( $var  ); mac_secondary=${vars[1]}

ip_primary=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["hostname"]]["internal_ip1"])'`
ip_secondary=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["hostname"]]["internal_ip2"])'`

sudo iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP
for bridge in `sudo ovs-vsctl show| grep Bridge| sed -E 's/ +Bridge //'| sed -E 's/"//g'`;
    do sudo ovs-vsctl del-br $bridge;
done

val=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["hostname"]])'`
region=${hostname:0:`expr ${#hostname} - 3`}
all_hosts=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); machines.pop(os.environ["hostname"], None); print(",".join(machines.keys()))'`

bridge_name=bridge
sudo ovs-vsctl add-br $bridge_name
var=$(ifconfig ${bridge_name}|grep ether); vars=( $var  ); mac_bridge=${vars[1]}
sudo ovs-vsctl add-port $bridge_name $iface_secondary
sudo ovs-ofctl del-flows $bridge_name
sudo ifconfig $bridge_name $ip_secondary/24 up
anycast_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $iface_secondary| tail -n1| egrep -o "[0-9]+"`
sudo ovs-ofctl add-flow $bridge_name in_port=local,actions=$anycast_port
sudo ovs-ofctl add-flow $bridge_name in_port=$anycast_port,actions=mod_dl_dst=${mac_bridge},local
# sudo ifconfig $iface_secondary down

# Setup the gre tunnel from router -> server
echo "setup router->server"
export server=${hostname:0:`expr ${#hostname} - 2`}sv
server_ip=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["server"]]["internal_ip1"])'`
server_local_port_name=server
server_gre_port_name=tunnel-server
echo sudo ovs-vsctl add-port $bridge_name $server_local_port_name -- set interface $server_local_port_name type=internal
sudo ovs-vsctl add-port $bridge_name $server_local_port_name -- set interface $server_local_port_name type=internal
echo sudo ovs-vsctl add-port $bridge_name $server_gre_port_name -- set interface $server_gre_port_name type=vxlan options:remote_ip=$server_ip
sudo ovs-vsctl add-port $bridge_name $server_gre_port_name -- set interface $server_gre_port_name type=vxlan options:remote_ip=$server_ip
echo sudo ifconfig $server_local_port_name 12.12.12.12/32 up
sudo ifconfig $server_local_port_name 12.12.12.12/32 up
server_gre_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $server_gre_port_name| tail -n1| egrep -o "[0-9]+"`
server_local_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $server_local_port_name| tail -n1| egrep -o "[0-9]+"`
echo sudo ovs-ofctl add-flow $bridge_name in_port=$server_gre_port,actions=mod_dl_src:${mac_secondary},$iface_secondary
sudo ovs-ofctl add-flow $bridge_name in_port=$server_gre_port,actions=mod_dl_src:${mac_secondary},$iface_secondary
echo sudo ovs-ofctl add-flow $bridge_name in_port=$server_local_port,actions=$server_gre_port
sudo ovs-ofctl add-flow $bridge_name in_port=$server_local_port,actions=$server_gre_port
echo sudo arp -s $ip_primary 00:00:00:00:00:00 -i $server_local_port_name
sudo arp -s $ip_primary 00:00:00:00:00:00 -i $server_local_port_name
echo sudo arp -s $ip_secondary 00:00:00:00:00:00 -i $server_local_port_name
sudo arp -s $ip_secondary 00:00:00:00:00:00 -i $server_local_port_name

# Setup the gre tunnel among routers
while IFS=',' read -ra ADDR
do
    echo "setup router->router"
    for remote_host in "${ADDR[@]}"
    do
        echo ${remote_host}
        dc_region=${remote_host:0:`expr ${#remote_host} - 3`}
        type=${remote_host:`expr ${#remote_host}` - 2:2}
        if [[ ${type} == rt ]] && [[ ${dc_region} != ${region} ]]
        then
            export remote_host
            remote_ip=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["remote_host"]]["external_ip1"])'`
            local_port_name=${dc_region:0:`expr ${#dc_region} - 1`}
            remote_port_name=tunnel-${dc_region_short}
            echo sudo ovs-vsctl add-port $bridge_name ${local_port_name} -- set interface ${local_port_name} type=internal
            sudo ovs-vsctl add-port $bridge_name ${local_port_name} -- set interface ${local_port_name} type=internal
            echo sudo ovs-vsctl add-port $bridge_name ${remote_port_name} -- set interface ${remote_port_name} type=vxlan options:remote_ip=${remote_ip}
            sudo ovs-vsctl add-port $bridge_name ${remote_port_name} -- set interface ${remote_port_name} type=vxlan options:remote_ip=${remote_ip}
            local_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $local_port_name| tail -n1| egrep -o "[0-9]+"`
            remote_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $remote_port_name| tail -n1| egrep -o "[0-9]+"`
            echo sudo ifconfig ${local_port_name} 12.12.12.12/32 up
            sudo ifconfig ${local_port_name} 12.12.12.12/32 up
            echo sudo ovs-ofctl add-flow ${bridge_name} in_port=${local_port},actions=${remote_port}
            sudo ovs-ofctl add-flow ${bridge_name} in_port=${local_port},actions=${remote_port}
            echo sudo ovs-ofctl add-flow ${bridge_name} in_port=${local_port},actions=${remote_port}
            sudo ovs-ofctl add-flow ${bridge_name} in_port=${remote_port},actions=${server_gre_port}
            echo sudo arp -s $ip_primary 00:00:00:00:00:00 -i ${local_port_name}
            sudo arp -s $ip_primary 00:00:00:00:00:00 -i ${local_port_name}
            echo sudo arp -s $ip_secondary 00:00:00:00:00:00 -i ${local_port_name}
            sudo arp -s $ip_secondary 00:00:00:00:00:00 -i ${local_port_name}
        fi
    done
done <<< $all_hosts

date > gre.sh.end_ts