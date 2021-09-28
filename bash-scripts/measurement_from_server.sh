hostname=`hostname`
main_test_ip="`jq -r .EXTERNAL_IP ~/data/server_settings.json`"
main_hostname=`jq -r .HOSTNAME ~/data/server_settings.json`

router_ips=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/machine.json")); print(" ".join([machines[x]["internal_ip1"] for x in machines if "router" in x]));'`)
server_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/machine.json")); print(" ".join([x for x in machines if "server" in x]));'`)
router_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/machine.json")); print(" ".join([x for x in machines if "router" in x]));'`)

ps -ef | grep "top -b -d 0.1" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
start_time=$(date "+%Y%m%d%H%M%S")
echo "start_time:" $start_time > ~/cpu.log
top -b -d 0.1 | grep -a '%Cpu' >> ~/cpu.log &

server_num=-1
for i in `seq 0 $((${#server_hostnames[*]} - 1))`
do
    if [[ ${server_hostnames[$i]} == $hostname ]] 
    then
        server_num=$i
    fi
done
echo "server_num: " $server_num > ~/server.log

router_ip=()
router_port=()
default_max=100
for i in `seq 0 $((${#router_ips[*]} - 1))`
do
    router_ip[$i]=${router_ips[$i]}
    router_port[$i]=$((5200 + $i + $server_num))
done
echo ${router_ip[*]}
echo ${router_port[*]}

throughput=()
max_throughput=0
second_max=0
sudo wondershaper clear ens4

rm -f /home/mininet/initial_*
tmux send-key -t main:2 "sudo LD_LIBRARY_PATH=/home/mininet/data /home/mininet/data/server --interface=ens4 --unicast=${server_ips[$server_num]} 0.0.0.0 4433 /home/mininet/data/server.key /home/mininet/data/server.crt -q" Enter

while [[ `ls -l /home/mininet/initial_* | wc -l` -lt 5 ]]
do
    sleep 10
done
echo "get all initial data!"

capable_ratio=()
std_ratio=()
max_capable_ratio=0
for i in `seq 0 $((${#router_ip[*]} - 1))`
do
    capable_ratio[i]=`cat /home/mininet/initial_${i}.txt`
    if [[ `echo "${capable_ratio[i]} > $max_capable_ratio" | bc` -eq 1  ]]
    then
        max_capable_ratio=${capable_ratio[i]}
    fi
done

rm -f /home/mininet/initial_std.txt
for i in `seq 0 $((${#router_ip[*]} - 1))`
do
    std_ratio[i]=`awk 'BEGIN{print "'${capable_ratio[i]}'" / "'$max_capable_ratio'"}'`
    echo "router_hostname: " ${router_hostnames[$i]} >> server.log
    echo "router std_ratio: " ${std_ratio[i]} >> server.log
    echo ${std_ratio[i]} >> /home/mininet/initial_std.txt
done

sudo wondershaper clear ens4
second_max=$((5*1024))

# if [[ ${server_hostnames[$server_num]} == "hestia-asia-southeast1-c-server" ]]
# then
#     second_max=$((10*1024))
# elif [[ ${server_hostnames[$server_num]} == "hestia-australia-southeast1-c-server" ]]
# then
#     second_max=$((15*1024))
# elif [[ ${server_hostnames[$server_num]} == "hestia-europe-west2-b-server" ]]
# then
#     second_max=$((35*1024))
# elif [[ ${server_hostnames[$server_num]} == "hestia-northamerica-northeast1-c-server" ]]
# then
#     second_max=$((20*1024))
# elif [[ ${server_hostnames[$server_num]} == "hestia-southamerica-east1-b-server" ]]
# then
#     second_max=$((5*1024))
# fi

# echo max_throughput: $max_throughput >> ~/server.log
echo "second_max: " $second_max >> ~/server.log
sudo wondershaper ens4 $second_max $second_max

while true
do
    cpu_idle_temp=`tail -2 /home/mininet/cpu.log | head -n 1 |awk -F',' '{print $4}'`
    cpu_idle=`echo $cpu_idle_temp | tr -cd "[0-9][.]"`
    # echo $cpu_idle

    # if [[ $cpu_idle == "id"* ]]
    # then 
        # cpu_idle=100.0
    # fi
    # echo $cpu_idle
    temp_now_used=`tac /home/mininet/iftop_log.txt | grep -a "Total send rate" |head -n 1| awk '{print $4}'`
    echo "temp_now_used: " $temp_now_used >> ~/server.log

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

    echo "now_used: " $now_used >> ~/server.log
    res_throughput=`awk 'BEGIN{print "'$second_max'" - "'$now_used'"}'`
    echo "res_throughput:" $res_throughput >> ~/server.log

    for i in `seq 0 $((${#router_ip[*]} - 1))`
    do
        # throughput_value=`awk 'BEGIN{print ("1" - "'$now_used'") * "'${throughput[$i]}'"}'`
        # echo throughput_value: $throughput_value >> ~/server.log

        if  [[ `echo "${capable_ratio[i]} < $res_throughput" | bc` -eq 1  ]]
        then
            echo "capable_ratio: " ${capable_ratio[i]} >> ~/server.log
            redis-cli -h ${router_ip[$i]} -a 'Hestia123456' set throughput_$hostname ${capable_ratio[i]} > /dev/null
        else
            exist_throughput=`python3 /home/mininet/data/init/get_n_video.py`
            echo "exist_throughput: " $exist_throughput >> ~/server.log
            valid_ratio=0.12
            avg_throughput=`awk 'BEGIN{print "'$second_max'" * "'$valid_ratio'" / ("'$exist_throughput'" + "'${std_ratio[i]}'") * "'${std_ratio[i]}'" }'`
            echo "avg_throughput: " $avg_throughput >> ~/server.log
            redis-cli -h ${router_ip[$i]} -a 'Hestia123456' set throughput_$hostname ${avg_throughput} > /dev/null
        fi
        
        redis-cli -h ${router_ip[$i]} -a 'Hestia123456' set cpu_idle_$hostname $cpu_idle > /dev/null
    done
    sleep 1.5
done