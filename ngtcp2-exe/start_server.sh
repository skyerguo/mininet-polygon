while getopts ":i:s:p:t:" opt
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
        ?)
            echo "未知参数"
            exit 1;;
    esac
done

echo $start_port >> temp_server.txt

for i in `seq $server_thread`
do 
    {
        port=$(($start_port+$i))
        echo server_$port >> temp_server.txt
        # echo sudo LD_LIBRARY_PATH=~/data ~/data/server --interface=ens4 --unicast=${unicast} 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q
        echo LD_LIBRARY_PATH=~/data ~/data/server --interface=server$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q >> temp_server.txt
        LD_LIBRARY_PATH=~/data ~/data/server --interface=server$server_id-eth0 --unicast=$server_ip 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q 1> temp_server_${server_id}_${port}_1.txt 2> temp_server_${server_id}_${port}_2.txt
    } &
done
