root_path=/proj/quic-PG0/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:n:a:" opt
do
    case $opt in
        i)
            dispatcher_id=$OPTARG
        ;;
        n)
            server_number=$OPTARG
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/competitiveness/'
            mkdir -p $measurement_result_path
        ;;
    esac
done


## 启动ngtcp2的client端，为第一次竞争力测量做准备
for server_id in `seq 0 $(($server_number - 1))`
do
    server_ip="10.0."$server_id".3"
    output_file=$measurement_result_path"dispatcher_"$dispatcher_id"_server_"$server_id

    echo sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $server_ip 4432 -i -p video -o 1 -w downloadinginit --client_ip "10.0."$dispatcher_id".5" --client_process 4433 --time_stamp 123456789 -q >> ${output_file}_1.txt

    sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $server_ip 4432 -i -p video -o 1 -w downloadinginit --client_ip "10.0."$dispatcher_id".5" --client_process 4433 --time_stamp 123456789 -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
done