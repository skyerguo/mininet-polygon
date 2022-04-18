root_path=/proj/quic-PG0/data
server_result_path=$root_path/result-logs/server/
respath=$root_path/result-logs/client/

while getopts ":i:s:p:t:a:m:n:" opt
do
    case $opt in
        i)
            server_id=$OPTARG
        ;;
        s)
            server_ip=$OPTARG
        ;;
        p)
            start_port=$OPTARG
        ;;
        t)
            server_thread=$OPTARG
        ;;
        a)
            server_result_path=${server_result_path}$OPTARG'/'$server_id'/'
            respath=${respath}$OPTARG'/'
            mkdir -p $server_result_path
        ;;
        m)
            mode=$OPTARG
        ;;
        n)
            redis_interface=$OPTARG
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
sudo ps -eLf | grep root | wc -l
# free -m
# sudo tcpdump udp -i s0-eth0 -w ${server_result_path}"tcpdump.cap" &


for i in `seq $server_thread`
do 
    {
        # temp_time=$((${RANDOM=$i} % 1000)) 
        # temp_time=`awk 'BEGIN{print "'$temp_time'" / "1000"}'`
        # sleep $temp_time
        port=$(($start_port+$i))
        output_file=${server_result_path}${server_id}'_'$port
        echo "output_file: " $output_file >> ${output_file}_tmp.txt

        echo "sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/server --interface=s$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port --redis_interface=s$server_id-eth$redis_interface --respath=$respath /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt" >> ${output_file}_tmp.txt
        sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/server --interface=s$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port --redis_interface=s$server_id-eth$redis_interface --respath=$respath /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
    } &
done
