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

## 以下所有流量相关的变量，单位均为Kb/sec
start_time=$(date "+%Y%m%d%H%M%S")

dispatcher_ip=() 
max_dispatcher_bw=0 ## 该server到所有dispatcher中，设定的最大流量
for i in `seq 0 $((${#dispatcher_ips[*]} - 1))`
do
    dispatcher_ip[$i]=${dispatcher_ips[$i]}
    dispatcher_bw[$i]=`awk 'BEGIN{print "'${dispatcher_bw[i]}'" * "1000"}'`
    if [[ `echo "${dispatcher_bw[i]} > $max_dispatcher_bw" | bc` -eq 1  ]]
    then
        max_dispatcher_bw=${dispatcher_bw[i]}
    fi
done

bw_competitiveness=() ## 流量竞争力，指每个dispatcher到server，一条传输流大概能占多少流量的能力。按照mininet设定的来做相对对比。
for i in `seq 0 $((${#dispatcher_ips[*]} - 1))`
do
    bw_competitiveness[i]=`awk 'BEGIN{print "'${dispatcher_bw[i]}'" / "'$max_dispatcher_bw'"}'`
done

output_file="${measurement_result_path}server/server_$server_id.log"

echo "dispatcher_ip: "${dispatcher_ip[*]} >> $output_file
echo "dispatcher_bw: "${dispatcher_bw[*]} >> $output_file
echo "bw_competitiveness: "${bw_competitiveness[*]} >> $output_file

echo "max_dispatcher_bw"$max_dispatcher_bw >> $output_file

server_pid=`ps aux | grep mininet:s${server_id} | grep -v grep | head -n 1 | awk '{print $2}'`
echo "server_pid: " $server_pid >> $output_file

echo "start_time: " $(date "+%Y-%m-%d-%H-%M-%S") "${measurement_result_path}server/cpu_$server_id.log"
top -p $server_pid -b -d 0.1 | grep -a '%Cpu' >> "${measurement_result_path}server/cpu_$server_id.log" & 

nload_path=$measurement_result_path"nload/"

while true
do
    cpu_idle_temp=`tail -2 ${measurement_result_path}server/cpu_$server_id.log | head -n 1 |awk -F',' '{print $4}'`
    cpu_idle=`echo $cpu_idle_temp | tr -cd "[0-9][.]"`

    ## 把文件从不可读的ANSI，通过sed替换编码改为可以用cat操作的常规编码
    echo "before file translation time", $(date "+%Y%m%d%H%M%S") >> $output_file
    for file_name in `ls ${nload_path}*$server_id.txt`
    do
        {
            new_file_name=${file_name//txt}"log"
            sed -e "s/\x1b\[[?]*[0-9]*[a-zA-Z]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b([a-zA-Z]//g; s/\x1b=//g; s/
/\r\n/g;"  $file_name > $new_file_name
        } &
    done
    echo "after file translation time", $(date "+%Y%m%d%H%M%S") >> $output_file

    for i in `seq 0 $((${#dispatcher_ip[*]} - 1))`
    do
        {
            output_file_2="${measurement_result_path}server/server_${server_id}_${i}.log"

            echo $(date "+%Y%m%d%H%M%S") >> $output_file_2

            ## 测量实时latency，并记录到redis中
            latency=`ping -i.2 -c5 ${dispatcher_ip[i]} | tail -1| awk '{print $4}' | cut -d '/' -f 2`
            echo "latency: "$latency >> $output_file_2
            redis-cli -h $redis_ip -a 'Hestia123456' set latency_s${server_id}_d$i $latency > /dev/null

            ## 通过计算所有对应zone的nload，最近5秒的平均带宽
            sum_existing_bw_per_zone=0  
            for file_name in `ls ${nload_path}*$i_$server_id.log`
            do
                existing_bw_per_client=`tail -n 10 $file_name | grep "Avg:" | head -n 1 | awk '{print $4}'`
                sum_existing_bw_per_zone=`awk 'BEGIN{print "'${sum_existing_bw_per_zone}'" + "'$existing_bw_per_client'"}'`
            done
            echo "sum_existing_bw_per_zone: " $sum_existing_bw_per_zone >> $output_file_2

            ## 计算如果加一条新的流量，可能可以使用的带宽大小
            ## 计算公式，总流量限制/(现有zone的所有流量+新的流量的竞争力*1)*新的流量的竞争力
            ## 流量竞争力，就用设定的流量来决定
            throughput_value=`awk 'BEGIN{print "'${dispatcher_bw[i]}'" / ("'${sum_existing_bw_per_zone}'" + "'${dispatcher_bw[i]}'") * "'${dispatcher_bw[i]}'"}'`
            echo "throughput_value: "$throughput_value >> $output_file_2
            redis-cli -h $redis_ip -a 'Hestia123456' set throughput_s${server_id}_d$i ${throughput_value} > /dev/null
        } &
    done
    
    echo $(date "+%Y%m%d%H%M%S") >> $output_file
    echo "cpu_idle: "$cpu_idle >> $output_file
    redis-cli -h $redis_ip -a 'Hestia123456' set cpu_s${server_id} ${cpu_idle} > /dev/null

    sleep 15
done
