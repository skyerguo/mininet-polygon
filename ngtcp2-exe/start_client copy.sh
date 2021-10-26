root_path=/data
client_result_path=$root_path/result-logs/client/

while getopts ":i:s:p:t:y:a:" opt
do
    case $opt in
        i)
            client_id=$OPTARG
        ;;
        s)
            # server_ip="10.0."$OPTARG".3"
            server_number=$OPTARG
        ;;
        p)
            # start_port=$OPTARG
            init_port=$OPTARG
        ;;
        t)
            client_thread=$OPTARG
        ;;
        y)
            server_thread=$OPTARG
        ;;
        a)
            client_result_path=${client_result_path}$OPTARG'/'
            mkdir -p $client_result_path
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

type_list=(${type_list_cpu[*]})

for i in `seq $client_thread`
do 
    {
        time_stamp=$(($(date +%s%N)/1000000))
        server_id=$((${RANDOM=$time_stamp} % $server_number))
        server_ip="10.0."$server_id".3"
        start_port=$(($init_port + $server_id * $server_thread))

        port=$(($start_port+$i))
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

        # echo client_$port >> temp_client.txt
        # echo LD_LIBRARY_PATH=~/data ~/data/client $server_ip $port -i -p normal_1 -o 1 -w google.com --client_ip $client_ip --client_process $port --time_stamp 1234567890 -q
        output_file=${client_result_path}${unique_identifier}
        echo "output_file: " $output_file >> ${output_file}_tmp.txt
        echo "data_type: " $data_type >> ${output_file}_tmp.txt
        echo "website: " $website >> ${output_file}_tmp.txt

        echo "sudo LD_LIBRARY_PATH=/data /data/client $server_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q" >> ${output_file}_tmp.txt

        temp_time=$((${RANDOM=$port} % 1000))
        temp_time=`awk 'BEGIN{print "'$temp_time'" / "1000"}'`
        echo "sleep_time: " $temp_time >> ${output_file}_tmp.txt
        sleep $temp_time

        sudo LD_LIBRARY_PATH=/data /data/client $server_ip $port -i -p $data_type -o 1 -w $website --client_ip $client_ip --client_process $port --time_stamp $time_stamp -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
    } &
done