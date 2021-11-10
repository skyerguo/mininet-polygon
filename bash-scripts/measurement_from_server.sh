root_path=/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:s:t:a:r:" opt
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
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/'
            mkdir -p $measurement_result_path
            mkdir -p ${measurement_result_path}"server"
        ;;
        r)
            redis_ip=$OPTARG
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

dispatcher_ips=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_dispatcher.json")); print(" ".join([machines[x]["internal_ip1"] for x in machines if "d" in x]));'`)
server_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_server.json")); print(" ".join([x for x in machines if "server" in x]));'`)
dispatcher_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_dispatcher.json")); print(" ".join([x for x in machines if "d" in x]));'`)
dispatcher_bw=(`echo $bw_set | tr '+' ' '`)

# echo "dispatcher_ips: " $dispatcher_ips
# echo "server_hostnames: " $server_hostnames
# echo "dispatcher_hostnames: " $dispatcher_hostnames

# ps -ef | grep "top -b -d 0.1" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
start_time=$(date "+%Y%m%d%H%M%S")
# echo "start_time:" $start_time > ~/cpu.log
# top -b -d 0.1 | grep -a '%Cpu' >> ~/cpu.log &


dispatcher_ip=()
dispatcher_port=()
default_max=100
for i in `seq 0 $((${#dispatcher_ips[*]} - 1))`
do
    dispatcher_ip[$i]=${dispatcher_ips[$i]}
    dispatcher_port[$i]=$((5200 + $i + $server_id))
    dispatcher_bw[$i]=$((${dispatcher_bw[i]} * 1000))
done
echo ${dispatcher_ip[*]}
echo ${dispatcher_port[*]}

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
# for i in `seq 0 $((${#dispatcher_ip[*]} - 1))`
# do
#     capable_ratio[i]=`cat /home/mininet/initial_${i}.txt`
#     if [[ `echo "${capable_ratio[i]} > $max_capable_ratio" | bc` -eq 1  ]]
#     then
#         max_capable_ratio=${capable_ratio[i]}
#     fi
# done

# rm -f /home/mininet/initial_std.txt
# for i in `seq 0 $((${#dispatcher_ip[*]} - 1))`
# do
#     std_ratio[i]=`awk 'BEGIN{print "'${capable_ratio[i]}'" / "'$max_capable_ratio'"}'`
#     echo "dispatcher_hostname: " ${dispatcher_hostnames[$i]} >> server.log
#     echo "dispatcher std_ratio: " ${std_ratio[i]} >> server.log
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
    temp_now_used=`tac ${measurement_result_path}iftop/iftop_log_$server_id.txt | grep -a "Total send rate" |head -n 1| awk '{print $4}'`
    
    if [ ! -n "$temp_now_used" ]; then
        sleep 1.5
        continue
    fi

    output_file="${measurement_result_path}server/server_$server_id.log"
    echo "time: " $(date "+%Y%m%d%H%M%S") >> $output_file
    echo "temp_now_used: " $temp_now_used >> $output_file
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

    echo "now_used: " $now_used >> $output_file
    res_throughput=`awk 'BEGIN{print "'$second_max'" - "'$now_used'"}'`
    echo "res_throughput:" $res_throughput >> $output_file

    for i in `seq 0 $((${#dispatcher_ip[*]} - 1))`
    do
        echo "dispatcher_log: dispatcher"$i >> $output_file
        echo "{dispatcher_bw[i]}: "${dispatcher_bw[i]} >> $output_file
        echo "res_throughput: "$res_throughput >> $output_file
        # if  [[ `echo "${dispatcher_bw[i]} < $res_throughput" | bc` -eq 1  ]]
        # then
        #     redis-cli -h "127.0.0.1" -a 'Hestia123456' set throughput_server${server_id}_dispatcher$i ${dispatcher_bw[i]} # > /dev/null
        # else
        #     exist_throughput=`python3 /home/mininet/mininet-polygon/py-scripts/get_n_video.py $server_id $i`
        #     echo "exist_throughput: "$exist_throughput

        #     avg_throughput=`awk 'BEGIN{print ("'${dispatcher_bw[i]}'" - "'$exist_throughput'") / "'${dispatcher_bw[i]}'" }'`
        #     echo "avg_throughput: "$avg_throughput 
        #     redis-cli -h "127.0.0.1" -a 'Hestia123456' set throughput_server${server_id}_dispatcher$i ${dispatcher_bw[i]} ${avg_throughput} # > /dev/null
        # fi
        exist_throughput=`python3 /home/mininet/mininet-polygon/py-scripts/get_n_video.py $server_id $i ${measurement_result_path}`
        echo "exist_throughput: "$exist_throughput >> $output_file

        avg_throughput=`awk 'BEGIN{print ("'${dispatcher_bw[i]}'" - "'$exist_throughput'") / "'${dispatcher_bw[i]}'" }'`
        echo "avg_throughput: "$avg_throughput >> $output_file
        redis-cli -h $redis_ip -a 'Hestia123456' set throughput_server${server_id}_dispatcher$i ${dispatcher_bw[i]} ${avg_throughput} # > /dev/null
        
        # redis-cli -h ${dispatcher_ip[$i]} -a 'Hestia123456' set cpu_idle_$hostname $cpu_idle > /dev/null
    done
    sleep 1.5
done