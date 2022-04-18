root_path=/proj/quic-PG0/data
dispatcher_result_path=$root_path/result-logs/dispatcher/

while getopts ":i:s:p:t:r:a:m:n:z:" opt
do
    case $opt in
        i)
            dispatcher_id=$OPTARG
        ;;
        s)
            server_number=$OPTARG
        ;;
        p)
            start_port=$OPTARG
        ;;
        t)
            dispatcher_thread=$OPTARG
        ;;
        a)
            dispatcher_result_path=${dispatcher_result_path}$OPTARG'/'$dispatcher_id'/'
            mkdir -p $dispatcher_result_path
        ;;
        r)
            redis_ip=$OPTARG
        ;;
        m)
            mode=$OPTARG
        ;;
        n)
            redis_interface=$OPTARG
        ;;
        z)
            dispatcher_zone=$OPTARG
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

# ulimit -SHu 330603 # 设置nproc即用户可以使用的进程数量
# ulimit -a
# pstree -p | wc -l
# ps -eLf | grep myzhou | wc -l
# sudo ps -eLf | grep root | wc -l

for i in `seq $dispatcher_thread`
do 
    {
        port=$(($start_port+$i))
        output_file=${dispatcher_result_path}${dispatcher_id}'_'$port
        echo "output_file: " $output_file >> ${output_file}_tmp.txt

        echo "sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/dispatcher --local_zone $dispatcher_zone d${dispatcher_id}-eth$server_number 0.0.0.0 $port /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt --redundancy 0 --current_dispatcher_name=d$dispatcher_id --redis_ip=$redis_ip --redis_interface=d$dispatcher_id-eth$redis_interface" >> ${output_file}_tmp.txt

        sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/dispatcher --local_zone $dispatcher_zone d${dispatcher_id}-eth$server_number 0.0.0.0 $port /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt --redundancy 0 --current_dispatcher_name=d$dispatcher_id --redis_ip=$redis_ip --redis_interface=d$dispatcher_id-eth$redis_interface -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
    } &
done
