## 当初始测量失败时，重新测量一次，获得competitiveness

root_path=/proj/quic-PG0/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:s:a:" opt
do
    case $opt in
        i)
            dispatcher_id=$OPTARG
        ;;
        s)
            server_id=$OPTARG
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/competitiveness/'
            mkdir -p $measurement_result_path
        ;;
    esac
done


server_ip="10.0."$server_id".3"
output_file=$measurement_result_path"dispatcher_"$dispatcher_id"_server_"$server_id

rm ${output_file}_1.txt ${output_file}_2.txt

echo sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $server_ip 4432 -i -p video -o 1 -w downloadinginit --client_ip "10.0."$dispatcher_id".5" --client_process 4433 --time_stamp 123456789 -q >> ${output_file}_1.txt

sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client $server_ip 4432 -i -p video -o 1 -w downloadinginit --client_ip "10.0."$dispatcher_id".5" --client_process 4433 --time_stamp 123456789 -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt