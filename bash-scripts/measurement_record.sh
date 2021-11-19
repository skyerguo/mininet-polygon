root_path=/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:r:a:" opt
do
    case $opt in
        i)
            dispatcher_id=$OPTARG
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/record/'
            mkdir -p ${measurement_result_path}
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

server_ips=(`python3 -c 'import json; import os; machines=json.load(open("/home/mininet/mininet-polygon/json-files/machine_server.json")); print(" ".join([machines[x]["internal_ip1"] for x in machines if "s" in x]));'`)


# server_ip=()
# for i in `seq 0 $((${#server_ips[*]} - 1))`
# do
#     server_ip[$i]=${server_ips[$i]}
# done

output_file=${measurement_result_path}$dispatcher_id'.log'
while true
do
    current_time=$(date "+%Y-%m-%d_%H:%M:%S")
    echo "current_time: " $current_time >> $output_file
    for i in `seq 0 $((${#server_ips[*]} - 1))`
    do
        throughput_record=`redis-cli -h $redis_ip -a 'Hestia123456' get throughput_server${i}_dispatcher${dispatcher_id}`
        cpu_record=`redis-cli -h $redis_ip -a 'Hestia123456' get cpu_server${i}_dispatcher${dispatcher_id}`        
        echo $i'+'$throughput_record'+'$cpu_record >> $output_file
    done
    sleep 1
done