root_path=/proj/quic-PG0/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:a:z:n:" opt
do
    case $opt in
        i)
            client_id=$OPTARG
            hostname="server"$server_id
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/'
            mkdir -p $measurement_result_path
            mkdir -p ${measurement_result_path}"nload"
        ;;
        z) 
            client_zone=$OPTARG
        ;;
        n)
            server_number=$OPTARG
        ;;
    esac
done

for i in `seq 0 $server_number`
do
    ## nload记录文件为nload_log_ca_czb_sc，根据client的interface，记录的是client_a到server_c的实时流量，按照cz_b，也就是dispatcher_b聚类。
    ## 每1000毫秒记录一次，全部数据每100秒刷新一次以防文件过长，按照kBit/s记录结果
    sudo nload -a 100 -u k nload -t 1000 -m devices c${client_id}-eth$i > ${measurement_result_path}nload/nload_log_c${client_id}_cz${client_zone}_s${i}.txt &
done
