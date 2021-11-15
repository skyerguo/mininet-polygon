root_path=/data
client_result_path=$root_path/result-logs/client/

while getopts ":i:s:p:t:y:r:a:m:" opt
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
            mkdir -p $client_result_path
        ;;
        m)
            mode=$OPTARG
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

client_ip="10.0.${client_id}.1"

type_list_all=("normal_1" "normal_1" "normal_1" "normal_1" "video" "video" "video" "video" "cpu") ## 4:4:1
type_list_normal=("normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1" "normal_1") ## 全是normal_1
type_list_video=("video" "video" "video" "video" "video" "video" "video" "video" "video") ## 全是video
type_list_cpu=("cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu" "cpu") ## 全是cpu

type_list=(${type_list_normal[*]})


for i in `seq $client_thread`
do 
    {
        time_stamp=$(($(date +%s%N)/1000000))
        dispatcher_id=$client_id ## 定死
        dispatcher_ip="10.0."$dispatcher_id".5"
        start_port=$init_port ## 定死
        
        port=$(($start_port+$i))
        output_file=${client_result_path}${client_id}'_'$port

        echo "output_file: " $output_file >> ${output_file}_tmp.txt

        if [[ $mode == "Polygon" ]]; then
            destination_ip="10.0."$client_id".5"
        elif [[ $mode == "DNS" ]]; then
            destination_ip="10.0."$client_id".3"
        elif [[ $mode == "Anycast" ]]; then
            destination_ip="10.0."$client_id".3"
        elif [[ $mode == "FastRoute" ]]; then
            destination_ip="10.0."$client_id".3"
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
        opt=1

        if [[ $data_type == "normal_1" ]]; then
            website="google.com"

        elif [[ $data_type == "video" ]]; then
            website="downloading"

        elif [[ $data_type == "cpu" ]]; then 
            website="cpu"
        fi
        
        echo "data_type: " $data_type >> ${output_file}_tmp.txt
        echo "website: " $website >> ${output_file}_tmp.txt

        # echo "sudo LD_LIBRARY_PATH=/data /data/client $dispatcher_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp" >> ${output_file}_tmp.txt

        temp_time=$((${RANDOM=$port} % 1000))
        temp_time=`awk 'BEGIN{print "'$temp_time'" / "1000"}'`
        echo "sleep_time: " $temp_time >> ${output_file}_tmp.txt
        sleep $temp_time

        # sudo LD_LIBRARY_PATH=/data /data/client $dispatcher_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
        sudo LD_LIBRARY_PATH=/data /data/client $destination_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt

        sleep 100

        current_jct=`tac ${output_file}_2.txt | grep -a "PLT" |head -n 1| awk '{print $2}'`

        redis-cli -h ${redis_ip} -a 'Hestia123456' -n 1 set 'jct_'${client_id}'_'$port $current_jct
    } &
done