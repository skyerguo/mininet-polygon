root_path=/home/mininet
client_result_path=$root_path/result-logs/client/
server_result_path=$root_path/result-logs/server/

# Useful values
while getopts ":i:s:p:t:" opt
do
    case $opt in
        i)
            client_id=$OPTARG
        ;;
        s)
            server_ip=$OPTARG
        ;;
        p)
            start_port=$OPTARG
        ;;
        t)
            client_thread=$OPTARG
        ;;
        ?)
            echo "未知参数"
            exit 1;;
    esac
done

echo $start_port >> temp_client.txt

for i in `seq $client_thread`
do 
    {
        port=$(($start_port+$i))
        echo client_$port >> temp_client.txt
        # echo sudo LD_LIBRARY_PATH=~/data ~/data/server --interface=ens4 --unicast=${unicast} 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q
        echo LD_LIBRARY_PATH=~/data ~/data/client $server_ip $port -i -p normal_1 -o 1 -w google.com --client_ip 10.0.0.1 --client_process $port --time_stamp 1234567890 -q
        LD_LIBRARY_PATH=~/data ~/data/client $server_ip $port -i -p normal_1 -o 1 -w google.com --client_ip 10.0.0.1 --client_process $port --time_stamp 1234567890 -q 1> temp_client_${client_id}_${port}_1.txt 2> temp_client_${client_id}_${port}_2.txt
    } &
done