while getopts ":i:" opt
do
    case $opt in
        i)
            dispatcher_id=$OPTARG
            hostname="d"$dispatcher_id
            dispatcher_ip="10.0."$dispatcher_id".5"
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

cd ${HOME}
root_path="/home/mininet/mininet-polygon/"
machine_server_path=$root_path"json-files/machine_server.json"
machine_dispatcher_path=$root_path"json-files/machine_dispatcher.json"

echo "hostname: "$hostname

iface_primary=$hostname'-eth0'
iface_secondary=$hostname'-eth1'
var=$(ifconfig ${iface_secondary}|grep ether); vars=( $var  ); mac_secondary=${vars[1]}
echo "mac_secondary: "$mac_secondary
# ip_primary=`python3 -c 'import json; machines=json.load(open("machine.json")); print(machines[machines["hostname"]]["internal_ip1"])'`
# ip_secondary=`python3 -c 'import json; machines=json.load(open("machine.json")); print(machines[machines["hostname"]]["internal_ip2"])'`
# sudo iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP
# for bridge in `sudo ovs-vsctl show| grep Bridge| sed -E 's/ +Bridge //'| sed -E 's/"//g'`;
#     do sudo ovs-vsctl del-br $bridge;
# done

# machines=`cat machine.json`

# hostname=`python3 -c 'import json; machines=json.load(open("machine.json")); print(machines["hostname"])'`
# region=${hostname:0:`expr ${#hostname} - 7`}
# all_hosts=`python3 -c 'import json; machines=json.load(open("machine.json")); machines.pop("hostname", None); print(",".join(machines.keys()))'`
ip_primary=$dispatcher_ip
ip_secondary=$dispatcher_ip


## GRE配置在switch上，而不是host上。

setup_dispatcher() {
    bridge_name="bridge-"$hostname
    sudo ovs-vsctl add-br $bridge_name
    sudo ovs-vsctl show
    var=$(ifconfig ${bridge_name}|grep ether); vars=( $var  ); mac_bridge=${vars[1]}
    echo "vars: "$vars
    echo "mac_bridge: "$mac_bridge
    echo "iface_secondary: "$iface_secondary
    sudo ovs-vsctl add-port $bridge_name $iface_secondary
    sudo ovs-ofctl del-flows $bridge_name
    return
    sudo ifconfig $bridge_name $ip_secondary/24 up
    anycast_port=`sudo ovs-vsctl -- --columns=name,ofport list Interface $iface_secondary| tail -n1| egrep -o "[0-9]+"`
    echo "anycast_port: "$anycast_port
    sudo ovs-ofctl add-flow $bridge_name in_port=local,actions=$anycast_port
    sudo ovs-ofctl add-flow $bridge_name in_port=$anycast_port,actions=mod_dl_dst=${mac_bridge},local
    return

    ## Setup the gre tunnel from dispatcher -> server
    echo "setup dispatcher->server"
    export server=${hostname:0:`expr ${#hostname} - 6`}server
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

    # Setup the gre tunnel among dispatchers
    while IFS=',' read -ra ADDR
    do
        echo "setup dispatcher->dispatcher"
        for remote_host in "${ADDR[@]}"
        do
            echo ${remote_host}
            dc_region=${remote_host:0:`expr ${#remote_host} - 7`}
            type=${remote_host:`expr ${#remote_host}` - 6:6}
            if [[ ${type} == dispatcher ]] && [[ ${dc_region} != ${region} ]]
            then
                export remote_host
                remote_ip=`python3 -c 'import os; import json; machines=json.load(open("machine.json")); print(machines[os.environ["remote_host"]]["external_ip1"])'`
                #dc_region_short=${dc_region//-/}
                export dc_region_short=${dc_region:7}
                dc_region_short=`python3 -c "import os; print('-'.join([''.join((t[:2], t[-2:])) for t in '${dc_region_short}'.split('-')[:2]]))"`
                local_port_name=$dc_region_short
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
}

# for bridge in `sudo ovs-vsctl show| grep Bridge| sed -E 's/ +Bridge //'| sed -E 's/"//g'`
# do
#     sudo ovs-vsctl del-br $bridge
# done

setup_dispatcher
