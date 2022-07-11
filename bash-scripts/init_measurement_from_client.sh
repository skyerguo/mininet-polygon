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
            dispatcher_id=$OPTARG
        ;;
        n)
            server_number=$OPTARG
        ;;
    esac
done

for i in `seq 0 $server_number`
do
    ## nload记录文件为nload_log_ca_czb_sc，根据client的interface，记录的是client_a到server_c的实时流量，按照cz_b，也就是dispatcher_b聚类。
    ## 每2000+毫秒记录一次，计算平均的数据按最近15秒算，按照kBit/s记录结果

    ## 刷新间隔，稍微错开一点，防止nload同时跑起来
    refresh_interval=`awk 'BEGIN{print "2000" + ("50" * "'$i'")}'`
    # echo "refresh_interval: " $refresh_interval
    sudo nload -a 100 -u k -t $refresh_interval -m devices c${client_id}-eth$i > ${measurement_result_path}nload/nload_log_c${client_id}_cz${dispatcher_id}_s${i}.txt &
    
    # # 错峰运行nload，防止I/O爆炸
    # temp_time=$((${RANDOM=$i} % 1000)) 
    # temp_time=`awk 'BEGIN{print "'$temp_time'" / "1000"}'`
    # sleep $temp_time
done
