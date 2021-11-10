while getopts ":i:s:t:" opt
do
    case $opt in
        i)
            server_id=$OPTARG
            hostname="server"$server_id
        ;;
        s)
            server_ip=$OPTARG
        ;;
        t)
            bw_set=$OPTARG
            # echo "bw_set:" $bw_set
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

router_ips=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_router.json")); print(" ".join([machines[x]["internal_ip1"] for x in machines if "router" in x]));'`)
server_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_server.json")); print(" ".join([x for x in machines if "server" in x]));'`)
router_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_router.json")); print(" ".join([x for x in machines if "router" in x]));'`)
router_bw=(`echo $bw_set | tr '+' ' '`)

# echo "router_ips: " $router_ips
# echo "server_hostnames: " $server_hostnames
# echo "router_hostnames: " $router_hostnames

# ps -ef | grep "top -b -d 0.1" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
start_time=$(date "+%Y%m%d%H%M%S")
# echo "start_time:" $start_time > ~/cpu.log
# top -b -d 0.1 | grep -a '%Cpu' >> ~/cpu.log &


router_ip=()
router_port=()
default_max=100
for i in `seq 0 $((${#router_ips[*]} - 1))`
do
    router_ip[$i]=${router_ips[$i]}
    router_port[$i]=$((5200 + $i + $server_id))
    router_bw[$i]=$((${router_bw[i]} * 1000))
done
# echo ${router_ip[*]}
# echo ${router_port[*]}

# throughput=()
# max_throughput=0
# second_max=0
# sudo wondershaper clear ens4

# rm -f /home/mininet/initial_*
# tmux send-key -t main:2 "sudo LD_LIBRARY_PATH=/home/mininet/data /home/mininet/data/server --interface=ens4 --unicast=${server_ips[$server_id]} 0.0.0.0 4433 /home/mininet/data/server.key /home/mininet/data/server.crt -q" Enter

# while [[ `ls -l /home/mininet/initial_* | wc -l` -lt 5 ]]
# do
#     sleep 10
# done
# echo "get all initial data!"

# capable_ratio=()
# std_ratio=()
# max_capable_ratio=0
# for i in `seq 0 $((${#router_ip[*]} - 1))`
# do
#     capable_ratio[i]=`cat /home/mininet/initial_${i}.txt`
#     if [[ `echo "${capable_ratio[i]} > $max_capable_ratio" | bc` -eq 1  ]]
#     then
#         max_capable_ratio=${capable_ratio[i]}
#     fi
# done

# rm -f /home/mininet/initial_std.txt
# for i in `seq 0 $((${#router_ip[*]} - 1))`
# do
#     std_ratio[i]=`awk 'BEGIN{print "'${capable_ratio[i]}'" / "'$max_capable_ratio'"}'`
#     echo "router_hostname: " ${router_hostnames[$i]} >> server.log
#     echo "router std_ratio: " ${std_ratio[i]} >> server.log
#     echo ${std_ratio[i]} >> /home/mininet/initial_std.txt
# done

# sudo wondershaper clear ens4
# second_max=$((5*1024))

# echo max_throughput: $max_throughput >> ~/server.log
# echo "second_max: " $second_max 
# sudo wondershaper ens4 $second_max $second_max

## 以下所有流量相关的变量，单位均为Kb/sec
second_max=$((100*1024)) # 假设每个节点最多100MB流量

while true
do
    # cpu_idle_temp=`tail -2 /home/mininet/cpu.log | head -n 1 |awk -F',' '{print $4}'`
    # cpu_idle=`echo $cpu_idle_temp | tr -cd "[0-9][.]"`

    temp_now_used=`tac /data/measurement_log/iftop/iftop_log_$server_id.txt | grep -a "Total send rate" |head -n 1| awk '{print $4}'`
    
    if [ ! -n "$temp_now_used" ]; then
        sleep 1.5
        continue
    fi

    echo "temp_now_used: " $temp_now_used >> "/data/measurement_log/server/server_$server_id.log"
    now_used=`echo $temp_now_used | tr -cd "[0-9][.]"`

    if [[ $temp_now_used == *"Mb" ]]
    then
        now_used=`awk 'BEGIN{print "'$now_used'" * "1000"}'`
    elif [[ $temp_now_used == *"Gb" ]]
    then
        now_used=`awk 'BEGIN{print "'$now_used'" * "1000000"}'`
    fi
    if [[ `echo "$now_used > $second_max" | bc` -eq 1 ]]
    then
        now_used=$second_max
    fi

    echo "now_used: " $now_used >> "/data/measurement_log/server/server_$server_id.log"
    res_throughput=`awk 'BEGIN{print "'$second_max'" - "'$now_used'"}'`
    echo "res_throughput:" $res_throughput >> "/data/measurement_log/server/server_$server_id.log"

    for i in `seq 0 $((${#router_ip[*]} - 1))`
    do
        echo "{router_bw[i]}: "${router_bw[i]}
        echo "res_throughput: "$res_throughput
        # if  [[ `echo "${router_bw[i]} < $res_throughput" | bc` -eq 1  ]]
        # then
        #     redis-cli -h "127.0.0.1" -a 'Hestia123456' set throughput_server${server_id}_router$i ${router_bw[i]} # > /dev/null
        # else
        #     exist_throughput=`python3 /home/mininet/mininet-polygon/py-scripts/get_n_video.py $server_id $i`
        #     echo "exist_throughput: "$exist_throughput

        #     avg_throughput=`awk 'BEGIN{print ("'${router_bw[i]}'" - "'$exist_throughput'") / "'${router_bw[i]}'" }'`
        #     echo "avg_throughput: "$avg_throughput 
        #     redis-cli -h "127.0.0.1" -a 'Hestia123456' set throughput_server${server_id}_router$i ${router_bw[i]} ${avg_throughput} # > /dev/null
        # fi
        exist_throughput=`python3 /home/mininet/mininet-polygon/py-scripts/get_n_video.py $server_id $i`
        echo "exist_throughput: "$exist_throughput

        avg_throughput=`awk 'BEGIN{print ("'${router_bw[i]}'" - "'$exist_throughput'") / "'${router_bw[i]}'" }'`
        echo "avg_throughput: "$avg_throughput 
        redis-cli -h 127.0.0.1 -a 'Hestia123456' set throughput_server${server_id}_router$i ${router_bw[i]} ${avg_throughput} # > /dev/null
        
        # redis-cli -h ${router_ip[$i]} -a 'Hestia123456' set cpu_idle_$hostname $cpu_idle > /dev/null
    done
    sleep 1.5
done