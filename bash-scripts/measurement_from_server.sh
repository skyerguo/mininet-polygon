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
total_bw_capability=0
for i in `seq 0 $((${#dispatcher_ips[*]} - 1))`
do
    dispatcher_ip[$i]=${dispatcher_ips[$i]}
    dispatcher_bw[$i]=`awk 'BEGIN{print "'${dispatcher_bw[i]}'" * "1000"}'`
    total_bw_capability=`awk 'BEGIN{print "'${total_bw_capability}'" + "'${dispatcher_bw[i]}'"}'`
done

output_file="${measurement_result_path}server/server_$server_id.log"

echo "dispatcher_ip: "${dispatcher_ip[*]} >> $output_file
echo "dispatcher_bw: "${dispatcher_bw[*]} >> $output_file

## 以下所有流量相关的变量，单位均为Kb/sec
echo "output_file: " $output_file >> $output_file

echo "total_bw_capability: " $total_bw_capability >> $output_file

server_pid=`ps aux | grep mininet:s${server_id} | grep -v grep | head -n 1 | awk '{print $2}'`
echo "server_pid: " $server_pid >> $output_file

echo "start_time: " $(date "+%Y-%m-%d-%H-%M-%S") "${measurement_result_path}server/cpu_$server_id.log"
top -p $server_pid -b -d 0.1 | grep -a '%Cpu' >> "${measurement_result_path}server/cpu_$server_id.log" & 

while true
do
    cpu_idle_temp=`tail -2 ${measurement_result_path}server/cpu_$server_id.log | head -n 1 |awk -F',' '{print $4}'`
    cpu_idle=`echo $cpu_idle_temp | tr -cd "[0-9][.]"`
    temp_now_used=`tac ${measurement_result_path}iftop/iftop_log_$server_id.txt | grep -a "Total send rate" |head -n 1| awk '{print $4}'`
    
    if [ ! -n "$temp_now_used" ]; then
        # sleep 1.5
        # continue
        temp_now_used=0
    fi

    echo "time: " $(date "+%Y-%m-%d-%H-%M-%S") >> $output_file
    echo "temp_now_used: " $temp_now_used >> $output_file
    now_used=`echo $temp_now_used | tr -cd "[0-9][.]"`

    if [[ $temp_now_used == *"Mb" ]]
    then
        now_used=`awk 'BEGIN{print "'$now_used'" * "1000"}'`
    elif [[ $temp_now_used == *"Gb" ]]
    then
        now_used=`awk 'BEGIN{print "'$now_used'" * "1000000"}'`
    fi
    if [[ `echo "$temp_now_used > $total_bw_capability" | bc` -eq 1 ]]
    then
        now_used=$total_bw_capability
    fi

    echo "now_used: " $now_used >> $output_file
    total_res_bw=`awk 'BEGIN{print "'$now_used'" / "'$total_bw_capability'"}'`
    echo "total_res_bw:" $total_res_bw >> $output_file
    total_res_rate=`awk 'BEGIN{print "1" - "'$total_res_bw'"}'`
    echo "total_res_rate:" $total_res_rate >> $output_file

    for i in `seq 0 $((${#dispatcher_ip[*]} - 1))`
    do
        echo "dispatcher_log: dispatcher"$i >> $output_file
        echo "{dispatcher_bw[i]}: "${dispatcher_bw[i]} >> $output_file

        # latency=`ping -i.2 -c5 ${dispatcher_ip[i]} | tail -1| awk '{print $4}' | cut -d '/' -f 2`
        
        ## exist_throughput 测量当前server到当前dispathcer的流量
        exist_throughput=`python3 /home/mininet/mininet-polygon/py-scripts/get_n_video.py $server_id $i ${measurement_result_path}`
        echo "exist_throughput: "$exist_throughput >> $output_file
        if [[ `echo "$exist_throughput > ${dispatcher_bw[i]}" | bc` -eq 1 ]]
        then
            exist_throughput=${dispatcher_bw[i]}
        fi

        # current_res_throughput=`awk 'BEGIN{print "'${dispatcher_bw[i]}'" - "'$exist_throughput'"}'`
        ## 总体逻辑：当前剩余 * (1-used/总)

        avg_throughput=`awk 'BEGIN{print ("'${dispatcher_bw[i]}'" - "'$exist_throughput'") * "'${total_res_rate}'"}'`
        echo "avg_throughput: "$avg_throughput >> $output_file
        redis-cli -h $redis_ip -a 'Hestia123456' set throughput_s${server_id}_d$i ${avg_throughput} > /dev/null

        # echo "latency: "$latency >> $output_file
        # redis-cli -h $redis_ip -a 'Hestia123456' set latency_server${server_id}_dispatcher$i ${latency} > /dev/null

        echo "cpu_idle: "$cpu_idle >> $output_file
        redis-cli -h $redis_ip -a 'Hestia123456' set cpu_s${server_id}_d$i ${cpu_idle} > /dev/null
        
        # redis-cli -h ${dispatcher_ip[$i]} -a 'Hestia123456' set cpu_idle_$hostname $cpu_idle > /dev/null
    done
    sleep 1.5
done