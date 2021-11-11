root_path=/data
dispatcher_result_path=$root_path/result-logs/dispatcher/

while getopts ":i:s:p:t:r:a:" opt
do
    case $opt in
        i)
            dispatcher_id=$OPTARG
        ;;
        s)
            dispatcher_ip=$OPTARG
        ;;
        p)
            start_port=$OPTARG
        ;;
        t)
            dispatcher_thread=$OPTARG
        ;;
        a)
            dispatcher_result_path=${dispatcher_result_path}$OPTARG'/'
            mkdir -p $dispatcher_result_path
        ;;
        r)
            redis_ip=$OPTARG
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

# sudo chown -R mininet:mininet ${dispatcher_result_path}
# echo sudo tcpdump udp -i d0-eth0 -w ${dispatcher_result_path}"tcpdump.cap"
# sudo tcpdump udp -i d0-eth0 -w ${dispatcher_result_path}"tcpdump.cap" &

for i in `seq $dispatcher_thread`
do 
    {
        port=$(($start_port+$i))
        output_file=${dispatcher_result_path}${dispatcher_id}'_'$port
        echo "output_file: " $output_file >> ${output_file}_tmp.txt

        echo "sudo LD_LIBRARY_PATH=/data /data/dispatcher --datacenter $dispatcher_id --user johnson --password johnson 'd'${dispatcher_id}'-eth0' 0.0.0.0 $port /data/server.key /data/server.crt --current_dispatcher_name 'd'$dispatcher_id" >> ${output_file}_tmp.txt

        sudo LD_LIBRARY_PATH=/data /data/dispatcher --datacenter $dispatcher_id --user johnson --password johnson "d"${dispatcher_id}"-eth0" 0.0.0.0 $port /data/server.key /data/server.crt --current_dispatcher_name "d"$dispatcher_id -q --redis_ip $redis_ip 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
        # sudo LD_LIBRARY_PATH=/data /data/server --interface=s$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port /data/server.key /data/server.crt -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
    } &
done
