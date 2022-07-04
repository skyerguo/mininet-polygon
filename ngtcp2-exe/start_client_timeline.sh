root_path=/proj/quic-PG0/data
client_result_path=$root_path/result-logs/client/
# saved_result_path=$root_path/saved_results/

while getopts ":i:p:t:r:a:m:z:d:o:c:" opt
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
            trace_filename='/proj/quic-PG0/data/trace_collection/'$OPTARG'.csv'
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
        o)
            outer_later=$OPTARG # 对当前的所在的zone，随机选择的一个outer_layer的server
            outer_later=$(($outer_later+1)) # 因为server0.example.com用来表示本机的IP，所以编号都要+1
        ;;
        c) ## 使用cpu
            trace_filename='/proj/quic-PG0/data/trace_collection/cpu_trace.csv'
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

trace_line=`cat $trace_filename | wc -l`

client_ip="10.0.${client_id}.1"

type_list_all=("normal_1" "normal_1" "normal_1" "normal_1" "video" "video" "video" "video" "cpu") ## 4:4:1，和gcloud保持一致
# type_list_all=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "video" "video" "video" "video" "video" "video" "video" "cpu") ## 7:7:1
type_list_normal=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1") ## 全是normal_1
type_list_video=("video" "video" "video" "video" "video" "video" "video" "video" "video") ## 全是video
type_list_cpu=("cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu") ## 全是cpu

if [[ $mode == "FastRoute" ]]; then
    dns_ip=`python3 -c "import os;import configparser;config = configparser.ConfigParser();config.read('/users/myzhou/mininet-polygon/FastRoute-files/ip.conf');dns_ip = config.get('DNS', 'inter');print(dns_ip)"`
    echo "dns_ip: " $dns_ip
    server_domain='server'$outer_later'.example.com'
    echo "server_domain: " $server_domain
fi

## 选择某一类的type_list
type_list=(${type_list_all[*]})
# type_list=(${type_list_cpu[*]})


for i in `seq $client_thread`
do
    {
        trace_start_line=`awk 'BEGIN{print "'$trace_line'" * "'$i'" * "0.1" + "'$client_id'"}'`
        trace_start_line=`printf "%.0f\n" $trace_start_line` # 取整
        trace_start_second=`cat $trace_filename | sed -n "$trace_start_line,${trace_start_line}p" | awk -F, '{print $1}'` 
        current_second=$(($(date +%s%N)/1000000000))
        trace_start_second=`awk 'BEGIN{print "'$current_second'" - "'$trace_start_second'"}'`
        echo "trace_start_line: "$trace_start_line
        # echo "trace_start_second: "$trace_start_second

        current_line=$trace_start_line
        for round in `seq 20000` ## 每秒一次
        do
            current_second=$(($(date +%s%N)/1000000000))
            relative_second=$(($current_second-$trace_start_second))
            current_line_second=`cat $trace_filename | sed -n "$current_line,${current_line}p" | awk -F, '{print $1}'` ## 注意单引号和双引号，前面必须是双引号，后面必须是单引号
            data_type=`cat $trace_filename | sed -n "$current_line,${current_line}p" | awk -F, '{print $2}'`
            data_type="cpu"

            ## 测试开始
            # echo "current_line: " $current_line
            # echo "current_line_second: "$current_line_second
            # echo "relative_second: "$relative_second
            # echo "data_type: "$data_type
            ## 测试结束

            if [[ $current_line_second > $relative_second ]]; then ## 如果有，则跳过
                sleep 1
                continue
            fi

            time_stamp=$(($(date +%s%N)/1000000))

            port=$(($init_port+$i))
            output_file=${client_result_path}${client_id}'_'$port'_'$time_stamp
            echo "output_file: " $output_file >> ${output_file}_tmp.txt
            echo "current_line" $current_line >> ${output_file}_tmp.txt

            if [[ $mode == "Polygon" ]]; then
                destination_ip="10.0."$client_zone".5"
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

            # # 错峰运行client，防止I/O爆炸
            # temp_time=$((${RANDOM=$port} % 2000)) 
            # temp_time=`awk 'BEGIN{print "'$temp_time'" / "2000"}'`
            # echo "sleep_time: " $temp_time >> ${output_file}_tmp.txt
            # sleep $temp_time

            current_time=$(date "+%Y-%m-%d_%H:%M:%S")
            echo "current_time: "$current_time >> ${output_file}_tmp.txt

            echo "nohup sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $destination_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q &" >> ${output_file}_tmp.txt
            nohup sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $destination_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt & 

            current_line=$(($current_line+1))
        done
    } &
done