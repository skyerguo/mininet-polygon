root_path=/data
client_result_path=$root_path/result-logs/client/
# saved_result_path=$root_path/saved_results/

while getopts ":i:s:p:t:d:y:r:a:m:" opt
do
    case $opt in
        i)
            client_id=$OPTARG
        ;;
        s)
            dispatcher_number=$OPTARG
        ;;
        p)
            init_port=$OPTARG
        ;;
        t)
            client_thread=$OPTARG
        ;;
        y)
            dispatcher_thread=$OPTARG
        ;;
        r)
            redis_ip=$OPTARG
        ;;
        a)
            client_result_path=${client_result_path}$OPTARG'/'
            # saved_result_path=${saved_result_path}$OPTARG'/'
            mkdir -p $client_result_path
        ;;
        m)
            mode=$OPTARG
            # saved_result_path=${saved_result_path}$mode'/'
        ;;
        d)
            dispatcher_id=$OPTARG # 通过zone，用参数传入dispatcher_id
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

client_ip="10.0.${client_id}.1"

type_list_all=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "video" "video" "video" "cpu") ## 5:3:1
type_list_normal=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1") ## 全是normal_1
type_list_video=("video" "video" "video" "video" "video" "video" "video" "video" "video") ## 全是video
type_list_cpu=("cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu") ## 全是cpu

dns_ip=`python3 -c "import os
import configparser
config = configparser.ConfigParser()
config.read('/home/mininet/mininet-polygon/FastRoute-files/ip.conf')
dns_ip = config.get('DNS', 'inter')
print(dns_ip)"`
echo "dns_ip: " $dns_ip

if [[ $client_id < 3 ]]; then ## 修改的话，需要对应修改LoadMonitory.py
    server_domain='server1.example.com'
else
    server_domain='server2.example.com'
fi
# echo "server_domain: " $server_domain

type_list=(${type_list_all[*]})
# type_list=(${type_list_video[*]})

for i in `seq $client_thread`
do
    {
        for round in `seq 2000`
        do
            time_stamp=$(($(date +%s%N)/1000000))
            # dispatcher_id=$client_id ## 定死
            dispatcher_ip="10.0."$dispatcher_id".5"
            start_port=$init_port ## 定死
            
            port=$(($start_port+$i))
            output_file=${client_result_path}${client_id}'_'$port'_'$time_stamp

            echo "output_file: " $output_file >> ${output_file}_tmp.txt
            # echo "current_time: "$time_stamp >> ${output_file}_tmp.txt

            if [[ $mode == "Polygon" ]]; then
                destination_ip="10.0."$client_id".5"
            elif [[ $mode == "DNS" ]]; then
                destination_ip="10.0."$client_id".3"
            elif [[ $mode == "Anycast" ]]; then
                destination_ip="10.0."$client_id".3"
            elif [[ $mode == "FastRoute" ]]; then
                destination_ip=`python3 -c "import dns.resolver;import os;dns_ip = '$dns_ip';my_resolver = dns.resolver.Resolver();my_resolver.nameservers = [dns_ip];DNS_resolving = my_resolver.query('$server_domain');print(DNS_resolving[0].to_text().split(' ')[0]);"`
            else
                echo "undefined mode!" >> ${output_file}_tmp.txt
                continue
            fi

            echo "mode: " $mode >> ${output_file}_tmp.txt
            echo "destination_ip: " $destination_ip >> ${output_file}_tmp.txt
            echo "destination_port: " $port >> ${output_file}_tmp.txt

            unique_identifier=${client_ip}'_'${port}'_'${time_stamp}
            rand_seed=$((${RANDOM=$port} % 9))
            data_type=${type_list[$rand_seed]}

            if [[ $data_type == "normal_1" ]]; then
                website="google.com"
                # sensitive_type="delay"

            elif [[ $data_type == "video" ]]; then
                website="downloadingcross"
                # sensitive_type="bw"

            elif [[ $data_type == "cpu" ]]; then 
                website="cpu"
                # sensitive_type="cpu"
            fi
            
            echo "data_type: " $data_type >> ${output_file}_tmp.txt
            echo "website: " $website >> ${output_file}_tmp.txt

            # temp_time=$((${RANDOM=$port} % 2000))
            # temp_time=`awk 'BEGIN{print "'$temp_time'" / "2000"}'`
            # echo "sleep_time: " $temp_time >> ${output_file}_tmp.txt
            # sleep $temp_time

            current_time=$(date "+%Y-%m-%d_%H:%M:%S")
            echo "current_time: "$current_time >> ${output_file}_tmp.txt

            echo "sudo LD_LIBRARY_PATH=/data /data/client $destination_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q" >> ${output_file}_tmp.txt
            sudo LD_LIBRARY_PATH=/data /data/client $destination_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt

            sleep 3
        done
    } &
done