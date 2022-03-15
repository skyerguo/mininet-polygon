root_path=/proj/quic-PG0/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:m:a:" opt
do
    case $opt in
        i)
            server_id=$OPTARG
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/'
            mkdir -p $measurement_result_path
            mkdir -p ${measurement_result_path}"competitiveness"
        ;;
        m)
            max_throughput=$OPTARG
        ;;
    esac
done

## 使用wondershaper，设置每个server进出口，最大的带宽总量
sudo wondershaper clear s$server_id-eth0
sudo wondershaper s$server_id-eth0 $max_throughput $max_throughput

server_ip="10.0."$server_id".3"
output_file=${measurement_result_path}"competitiveness/server_"$server_id
## 启动ngtcp2的server端，为第一次竞争力测量做准备
echo sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/server --interface=s$server_id-eth0 --unicast=$server_ip 0.0.0.0 4432 /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt >> ${output_file}_1.txt
sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/server --interface=s$server_id-eth0 --unicast=$server_ip 0.0.0.0 4432 /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt