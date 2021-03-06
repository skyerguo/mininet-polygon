root_path=/data
server_result_path=$root_path/result-logs/server/

while getopts ":i:s:p:t:a:" opt
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
            server_result_path=${server_result_path}$OPTARG'/'
            mkdir -p $server_result_path
        ;;
        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

for i in `seq $server_thread`
do 
    {
        port=$(($start_port+$i))
        # echo sudo LD_LIBRARY_PATH=~/data ~/data/server --interface=ens4 --unicast=${unicast} 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q
        # echo LD_LIBRARY_PATH=~/data ~/data/server --interface=server$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q >> temp_server.txt
        output_file=${server_result_path}${server_id}'_'$port
        echo "output_file: " $output_file >> ${output_file}_tmp.txt

        echo "sudo LD_LIBRARY_PATH=/data /data/server --interface=server$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port /data/server.key /data/server.crt -q " >> ${output_file}_tmp.txt
        sudo LD_LIBRARY_PATH=/data /data/server --interface=server$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port /data/server.key /data/server.crt -q 1>> ${output_file}_1.txt 2>> ${output_file}_2.txt
    } &
done
