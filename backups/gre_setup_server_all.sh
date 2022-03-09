root_path="/users/myzhou/mininet-polygon/"
date > ${root_path}timestamp-records/gre.server.sh.start_ts

## 删除现有的路由表
sudo iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP
for bridge in `sudo ovs-vsctl show| grep Bridge| sed -E 's/ +Bridge //'| sed -E 's/"//g'`
do
    sudo ovs-vsctl del-br $bridge
done

## setup Gre tunnel server -> router

export machine_server_path="../json-files/machine_server.json"

#get routers
routers=(`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(" ".join([item for item in machines.keys() if item.endswith("rt")]))'`)
pure_routers=(`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(" ".join([item.replace("_","") for item in machines.keys() if item.endswith("rt")]))'`)

for i in `seq 0 $((${#routers[*]} - 1))`
do
    # hostname=${routers[$i]}
    export router=${routers[$i]}
    router_primary_ip_inner=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(machines[os.environ["router"]]["internal_ip1"])'`
    router_secondary_ip_inner=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(machines[os.environ["router"]]["internal_ip2"])'`
    # echo "bridge: " $bridge
    router_bridge_name="router-"${pure_routers[$i]} # 不能有下划线，所有bridge和port名字，都用去掉下划线的
    router_port_name="tunnel-router-"${pure_routers[$i]}
    router_ip=$router_primary_ip_inner
    router_anycast_ip=$router_secondary_ip_inner
    sudo ovs-vsctl add-br $router_bridge_name
    sudo ovs-vsctl add-port $router_bridge_name $router_port_name -- set interface $router_port_name type=vxlan, options:remote_ip=$router_ip
    router_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $router_port_name| tail -n1| egrep -o "[0-9]+"`
    sudo ifconfig $router_bridge_name $router_anycast_ip/32 up
    var=`ifconfig ${router_bridge_name}| grep ether`
    vars=( $var )
    # echo "vars: " $vars
    router_mac=${vars[1]}
    sudo ovs-ofctl del-flows $router_bridge_name
    sudo ovs-ofctl add-flow $router_bridge_name in_port=$router_port,actions=mod_dl_dst:${router_mac},mod_nw_dst:${router_anycast_ip},local
    sudo ovs-ofctl add-flow $router_bridge_name in_port=local,actions=$router_port
    sudo arp -s $router_primary_ip_inner 00:00:00:00:00:00 -i $router_bridge_name
    sudo ip route flush table 2 > /dev/null 2>&1
    sudo ip rule delete table 2  > /dev/null 2>&1
    sudo ip route add default via $router_anycast_ip dev $router_bridge_name tab 2 > /dev/null 2>&1
    sudo ip rule add from $router_anycast_ip/32 tab 2 priority 600  > /dev/null 2>&1
    # break
done
# sudo ovs-vsctl show

date > ${root_path}timestamp-records/gre.server.sh.end_ts