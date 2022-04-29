root_path=/proj/quic-PG0/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:s:t:a:r:m:" opt
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
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/'
            mkdir -p $measurement_result_path
            mkdir -p ${measurement_result_path}"server"
        ;;
        r)
            redis_ip=$OPTARG
        ;;
        m)
            max_throughput=$OPTARG
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

dispatcher_ips=(`python3 -c 'import json; import os; machines=json.load(open("/users/myzhou/mininet-polygon/json-files/machine_dispatcher.json")); print(" ".join([machines[x]["internal_ip1"] for x in machines if "d" in x]));'`)
server_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/users/myzhou/mininet-polygon/json-files/machine_server.json")); print(" ".join([x for x in machines if "server" in x]));'`)
dispatcher_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/users/myzhou/mininet-polygon/json-files/machine_dispatcher.json")); print(" ".join([x for x in machines if "d" in x]));'`)
## 在mininet中设置的链路值，当前server到所有的dispatcher
dispatcher_bw=(`echo $bw_set | tr '+' ' '`)

## 以下所有流量相关的变量，单位均为Kbit/sec
start_time=$(date "+%Y%m%d%H%M%S")

raw_bw_competitiveness=`sed -n "$(($server_id+1)),$(($server_id+1))p" ${measurement_result_path}competitiveness/competitiveness.txt` ## 从文件读取的，当前server_id对应行的流量竞争力
bw_competitiveness=(`echo $raw_bw_competitiveness`) ## 流量竞争力，指每个dispatcher到server，一条传输流大概能占多少流量的能力。按照mininet设定的来做相对对比。

output_file="${measurement_result_path}server/server_s$server_id.log"

echo "dispatcher_ips: "${dispatcher_ips[*]} >> $output_file
echo "dispatcher_bw: "${dispatcher_bw[*]} >> $output_file
echo "bw_competitiveness: "${bw_competitiveness[*]} >> $output_file

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
    for file_name in `ls ${nload_path}*$server_id.txt`
    do
        new_file_name=${file_name//txt}"log"
        sudo bash /users/myzhou/mininet-polygon/bash-scripts/translate_nloads_file.sh -o $file_name -n $new_file_name
    done

    for dispatcher_id in `seq 0 $((${#dispatcher_ips[*]} - 1))`
    do
        {
            ## 用来记录以server_id和dispatcher_id为关键字的记录文件，以避免多进程并行导致的log记录错乱问题
            output_file_2="${measurement_result_path}server/server_s${server_id}_d${dispatcher_id}.log"

            echo "current_time: "$(date "+%Y%m%d%H%M%S") >> $output_file_2

            ## 测量实时latency，并记录到redis中
            latency=`ping -i.2 -c5 ${dispatcher_ips[dispatcher_id]} | tail -1| awk '{print $4}' | cut -d '/' -f 2`
            echo "latency: "$latency >> $output_file_2
            redis-cli -h $redis_ip -a 'Hestia123456' set latency_s${server_id}_d${dispatcher_id} $latency > /dev/null

            ## 通过计算所有对应zone的nload，最近15秒(根据nload -a x决定的x秒)的平均带宽
            sum_existing_bw_per_zone=0  
            for file_name in `ls ${nload_path}*cz${dispatcher_id}_s${server_id}.log`
            do
                existing_bw_per_client=`tail -n 10 $file_name | grep "Avg:" | head -n 1 | awk '{print $2}'` ## 因为从client记的，所以解析入流量
                echo "existing_bw_per_client: "$existing_bw_per_client >> $output_file_2
                sum_existing_bw_per_zone=`awk 'BEGIN{print "'${sum_existing_bw_per_zone}'" + "'$existing_bw_per_client'"}'`
            done
            echo "sum_existing_bw_per_zone: " $sum_existing_bw_per_zone >> $output_file_2

            ## 计算如果加一条新的流量，可能可以使用的带宽大小
            ## 计算公式，总流量限制/(现有zone的所有流量+新的流量的竞争力*1)*新的流量的竞争力
            ## 流量竞争力，就用设定的流量来决定
            valid_ratio=0.12 ## 虽然用wondershaper设定了最大值，但是实际上每条流最多用到"限制*valid_ratio"这么多的流量

            ## 用来检查throughput_value有没有算对的log。（已验证正确)
            # echo "max_throughput: " $max_throughput >> $output_file_2
            # echo "bw_competitiveness[$dispatcher_id]" ${bw_competitiveness[dispatcher_id]} >> $output_file_2

            throughput_value=`awk 'BEGIN{print "'$max_throughput'" * "'$valid_ratio'" / ("'${sum_existing_bw_per_zone}'" + "'${bw_competitiveness[dispatcher_id]}'") * "'${bw_competitiveness[dispatcher_id]}'"}'`
            echo "throughput_value: "$throughput_value >> $output_file_2
            redis-cli -h $redis_ip -a 'Hestia123456' set throughput_s${server_id}_d${dispatcher_id} ${throughput_value} > /dev/null
        } &
    done
    
    echo "current_time: "$(date "+%Y%m%d%H%M%S") >> $output_file
    echo "cpu_idle: "$cpu_idle >> $output_file
    redis-cli -h $redis_ip -a 'Hestia123456' set cpu_s${server_id} ${cpu_idle} > /dev/null

    sleep 15
done
