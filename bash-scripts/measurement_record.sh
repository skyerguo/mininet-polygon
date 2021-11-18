root_path=/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:r:a:" opt
do
    case $opt in
        i)
            server_id=$OPTARG
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/'
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


dispatcher_ip=()
for i in `seq 0 $((${#dispatcher_ips[*]} - 1))`
do
    dispatcher_ip[$i]=${dispatcher_ips[$i]}
done


while true
do
    current_time=$(date "+%Y-%m-%d_%H:%M:%S")
    for i in `seq 0 $((${#dispatcher_ip[*]} - 1))`
    do
        throughput_record=`redis-cli -h $redis_ip -a 'Hestia123456' get throughput_server${server_id}_dispatcher$i`

        cpu_record=`redis-cli -h $redis_ip -a 'Hestia123456' get cpu_server${server_id}_dispatcher$i`        
    done
    sleep 1
done