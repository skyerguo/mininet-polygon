cd ${HOME}

root_path="/home/mininet/mininet-polygon/"
# date > ${root_path}timestamp-records/gre.router.sh.start_ts

## 删除现有的路由表，server_all已经删了，这里不需要了
# sudo iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP
# for bridge in `sudo ovs-vsctl show| grep Bridge| sed -E 's/ +Bridge //'| sed -E 's/"//g'`
# do
#     sudo ovs-vsctl del-br $bridge
# done

## setup Gre tunnel server -> router

# export machine_server_path=$root_path"json-files/machine_server.json"
# export machine_router_path=$root_path"json-files/machine_router.json"
# echo "machine_server_path: "$machine_server_path

## get routers
# routers=(`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(" ".join([item for item in machines.keys() if item.endswith("rt")]))'`)
# servers=(`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(" ".join([item for item in machines.keys() if item.endswith("sv")]))'`)
# pure_routers=(`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(" ".join([item.replace("_","") for item in machines.keys() if item.endswith("rt")]))'`) # 将router的下划线去除
# pure_servers=(`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(" ".join([item.replace("_","") for item in machines.keys() if item.endswith("sv")]))'`) # 将server的下划线去除
servers=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_server.json")); print(" ".join([x for x in machines if "server" in x]));'`)
routers=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_router.json")); print(" ".join([x for x in machines if "router" in x]));'`)

for i in `seq 0 $((${#routers[*]} - 1))`
do
    # export hostname=$(ifconfig | head -1 | cut -d'-' -f1)
    echo "server $i:  " ${servers[i]}
    echo "router $i:  " ${routers[i]}
    export hostname=${routers[i]}
    iface_secondary=${hostname}'-eth0'
    echo "iface_secondary: "$iface_secondary
    # iface_secondary='s1-eth'$(($i*2+1))
    var=$(ifconfig ${iface_secondary}|grep ether); vars=( $var ); mac_secondary=${vars[1]}
    echo "mac_secondary: "$mac_secondary
    continue

    ip_primary=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(machines[os.environ["hostname"]]["internal_ip1"])'`
    ip_secondary=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(machines[os.environ["hostname"]]["internal_ip2"])'`

    val=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(machines[os.environ["hostname"]])'`
    region=${hostname:0:`expr ${#hostname} - 3`}
    # echo "region: "$region
    all_hosts=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); machines.pop(os.environ["hostname"], None); print(",".join(machines.keys()))'`
    # echo "all_hosts: "$all_hosts
    # break

    bridge_name="bridge-"${pure_routers[$i]}
    sudo ovs-vsctl add-br $bridge_name
    var=$(ifconfig ${bridge_name}|grep ether); vars=( $var ); mac_bridge=${vars[1]}
    sudo ovs-vsctl add-port $bridge_name $iface_secondary
    sudo ovs-ofctl del-flows $bridge_name
    sudo ifconfig $bridge_name $ip_secondary/24 up
    anycast_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $iface_secondary| tail -n1| egrep -o "[0-9]+"`
    sudo ovs-ofctl add-flow $bridge_name in_port=local,actions=$anycast_port
    sudo ovs-ofctl add-flow $bridge_name in_port=$anycast_port,actions=mod_dl_dst=${mac_bridge},local

    # Setup the gre tunnel from router -> server
    echo "setup router->server"
    # export server=${hostname:0:`expr ${#hostname} - 2`}sv
    export server=${servers[$i]}
    server_ip=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(machines[os.environ["server"]]["internal_ip1"])'`
    server_local_port_name="server-"${pure_servers[$i]}
    server_gre_port_name="tunnel-server-"${pure_servers[$i]}
    # echo "server_ip: "$server_ip
    # echo "server_local_port_name: "$server_local_port_name
    # echo "server_gre_port_name: "$server_gre_port_name

    # echo sudo ovs-vsctl add-port $bridge_name $server_local_port_name -- set interface $server_local_port_name type=internal
    sudo ovs-vsctl add-port $bridge_name $server_local_port_name -- set interface $server_local_port_name type=internal
    # echo sudo ovs-vsctl add-port $bridge_name $server_gre_port_name -- set interface $server_gre_port_name type=vxlan options:remote_ip=$server_ip
    sudo ovs-vsctl add-port $bridge_name $server_gre_port_name -- set interface $server_gre_port_name type=vxlan options:remote_ip=$server_ip
    # echo sudo ifconfig $server_local_port_name 12.12.12.12/32 up
    sudo ifconfig $server_local_port_name 12.12.12.12/32 up
    server_gre_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $server_gre_port_name| tail -n1| egrep -o "[0-9]+"`
    server_local_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $server_local_port_name| tail -n1| egrep -o "[0-9]+"`
    # echo sudo ovs-ofctl add-flow $bridge_name in_port=$server_gre_port,actions=mod_dl_src:${mac_secondary},$iface_secondary
    sudo ovs-ofctl add-flow $bridge_name in_port=$server_gre_port,actions=mod_dl_src:${mac_secondary},$iface_secondary
    # echo sudo ovs-ofctl add-flow $bridge_name in_port=$server_local_port,actions=$server_gre_port
    sudo ovs-ofctl add-flow $bridge_name in_port=$server_local_port,actions=$server_gre_port
    # echo sudo arp -s $ip_primary 00:00:00:00:00:00 -i $server_local_port_name
    sudo arp -s $ip_primary 00:00:00:00:00:00 -i $server_local_port_name
    # echo sudo arp -s $ip_secondary 00:00:00:00:00:00 -i $server_local_port_name
    sudo arp -s $ip_secondary 00:00:00:00:00:00 -i $server_local_port_name


    # Setup the gre tunnel among routers
    echo "setup router->router"

    # 把local的操作从下面的for提取出来，只用操作一次就可以了。
    local_port_name="dc-"${pure_routers[$i]}
    echo "local_port_name: "$local_port_name
    sudo ovs-vsctl add-port $bridge_name ${local_port_name} -- set interface ${local_port_name} type=internal
    local_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $local_port_name| tail -n1| egrep -o "[0-9]+"`
    sudo ifconfig ${local_port_name} 12.12.12.12/32 up

    IFS=',' read -ra ADDR <<< $all_hosts
    for remote_host in "${ADDR[@]}"
    do
        # echo "remote_host: "$remote_host
        dc_region=${remote_host:0:`expr ${#remote_host} - 3`}
        type=${remote_host:`expr ${#remote_host}` - 2:2}
        pure_remote_host=`echo $remote_host | sed 's/_//g'`
        # echo "pure_remote_host: "$pure_remote_host
        # echo "dc_region: "$dc_region
        # echo "type: "$type
        if [[ ${type} == rt ]] && [[ ${dc_region} != ${region} ]]
        then
            export remote_host
            remote_ip=`python3 -c 'import os; import json; machines=json.load(open(os.environ["machine_server_path"])); print(machines[os.environ["remote_host"]]["external_ip1"])'` ## 这里external_ip改了，都用internal_ip
            remote_port_name="tunnel-dc-"${pure_routers[$i]}"-"${pure_remote_host} ## 由于统一管理，这里需要记录源router信息+remote信息

            echo "remote_port_name: "$remote_port_name
            
            echo sudo ovs-vsctl add-port $bridge_name ${remote_port_name} -- set interface ${remote_port_name} type=vxlan options:remote_ip=${remote_ip}
            sudo ovs-vsctl add-port $bridge_name ${remote_port_name} -- set interface ${remote_port_name} type=vxlan options:remote_ip=${remote_ip} 
            # TODO 这里有大问题，如果还用同样的ip，会导致这里的bridge和gre_setup_server_all里的router-xxx ip冲突。但是mininet只有一个ip。
            continue
            remote_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $remote_port_name| tail -n1| egrep -o "[0-9]+"`
            # echo sudo ovs-ofctl add-flow ${bridge_name} in_port=${local_port},actions=${remote_port}
            sudo ovs-ofctl add-flow ${bridge_name} in_port=${local_port},actions=${remote_port}
            # echo sudo ovs-ofctl add-flow ${bridge_name} in_port=${local_port},actions=${remote_port}
            sudo ovs-ofctl add-flow ${bridge_name} in_port=${remote_port},actions=${server_gre_port}
            # echo sudo arp -s $ip_primary 00:00:00:00:00:00 -i ${local_port_name}
            sudo arp -s $ip_primary 00:00:00:00:00:00 -i ${local_port_name}
            # echo sudo arp -s $ip_secondary 00:00:00:00:00:00 -i ${local_port_name}
            sudo arp -s $ip_secondary 00:00:00:00:00:00 -i ${local_port_name}
        fi
    done
    # done <<< $all_hosts
    break
done

# date > ${root_path}timestamp-records/gre.router.sh.end_ts