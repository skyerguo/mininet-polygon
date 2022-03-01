root_path=/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:m:" opt
do
    case $opt in
        i)
            server_id=$OPTARG
            hostname="server"$server_id
        ;;
        m)
            max_throughput=$OPTARG
        ;;
    esac
done

## 使用wondershaper，设置每个server进出口，最大的带宽总量
s$server_id sudo wondershaper clear s$server_id-eth0
s$server_id sudo wondershaper s$server_id-eth0 $max_throughput $max_throughput

## 启动ngtcp2，做第一次竞争力测量
