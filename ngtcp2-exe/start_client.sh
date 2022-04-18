root_path=/proj/quic-PG0/data
client_result_path=$root_path/result-logs/client/
# saved_result_path=$root_path/saved_results/

while getopts ":i:p:t:r:a:m:z:d:" opt
do
    case $opt in
        i)
            client_id=$OPTARG
        ;;
        p)
            init_port=$OPTARG
        ;;
        t)
            client_thread=$OPTARG
        ;;
        r)
            redis_ip=$OPTARG
        ;;
        a)
            client_result_path=${client_result_path}$OPTARG'/'$client_id'/'
            mkdir -p $client_result_path
        ;;
        m)
            mode=$OPTARG
        ;;
        z)
            client_zone=$OPTARG # 通过client_zone，用参数传入需要转发给的dispatcher
        ;;
        d)
            des_server_id=$OPTARG # 随机选择的，同一个zone的server_id
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

# ulimit -SHu 330603 # 设置nproc即用户可以使用的进程数量

client_ip="10.0.${client_id}.1"

# type_list_all=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "video" "video" "video" "cpu") ## 5:3:1
type_list_all=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "video" "video" "video" "video" "video" "video" "video" "cpu") ## 7:7:1
type_list_normal=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1") ## 全是normal_1
type_list_video=("video" "video" "video" "video" "video" "video" "video" "video" "video") ## 全是video
type_list_cpu=("cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu") ## 全是cpu

if [[ $mode == "DNS" ]]; then
    dns_ip=`python3 -c "import os
    import configparser
    config = configparser.ConfigParser()
    config.read('/users/myzhou/mininet-polygon/FastRoute-files/ip.conf')
    dns_ip = config.get('DNS', 'inter')
    print(dns_ip)"`
    echo "dns_ip: " $dns_ip
fi

if [[ $client_id < 3 ]]; then ## 修改的话，需要对应修改LoadMonitory.py
    server_domain='server1.example.com'
else
    server_domain='server2.example.com'
fi

## 选择某一类的type_list
type_list=(${type_list_all[*]})
# type_list=(${type_list_cpu[*]})
# ulimit -a
# ps -eLf | wc -l
# echo "process now number:"
# ps --no-headers auxwwwm | cut -f1 -d' ' | sort | uniq -c | sort -n # 查看线程数
# echo "system file limitation"
# sysctl fs.file-nr # 查看系统file数限制
# echo "file now use"
# lsof -u myzhou 2>/dev/null | wc -l # 查看file使用

for i in `seq $client_thread`
do
    {
        for round in `seq 2000`
        do
            time_stamp=$(($(date +%s%N)/1000000))
            port=$(($init_port+$i))
            output_file=${client_result_path}${client_id}'_'$port'_'$time_stamp
            echo "output_file: " $output_file >> ${output_file}_tmp.txt
            # echo "current_time: "$time_stamp >> ${output_file}_tmp.txt

            if [[ $mode == "Polygon" ]]; then
                destination_ip="10.0."$client_zone".5"
            elif [[ $mode == "DNS" ]]; then
                destination_ip="10.0."$client_zone".3"
            elif [[ $mode == "Anycast" ]]; then
                destination_ip="10.0."$des_server_id".3"
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
            rand_seed=$((${RANDOM=$port} % ${#type_list[*]}))
            data_type=${type_list[$rand_seed]}

            if [[ $data_type == "normal_1" ]]; then
                website="google.com"
            elif [[ $data_type == "video" ]]; then
                # website="downloadingcross"
                website="downloading" ## 5M的文件
            elif [[ $data_type == "cpu" ]]; then 
                website="cpu"
            fi
            
            echo "data_type: " $data_type >> ${output_file}_tmp.txt
            echo "website: " $website >> ${output_file}_tmp.txt``

            # 错峰运行client，防止I/O爆炸
            temp_time=$((${RANDOM=$port} % 2000)) 
            temp_time=`awk 'BEGIN{print "'$temp_time'" / "2000"}'`
            echo "sleep_time: " $temp_time >> ${output_file}_tmp.txt
            sleep $temp_time

            current_time=$(date "+%Y-%m-%d_%H:%M:%S")
            echo "current_time: "$current_time >> ${output_file}_tmp.txt

            echo "sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $destination_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q" >> ${output_file}_tmp.txt
            sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $destination_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt

        done
    } &
done