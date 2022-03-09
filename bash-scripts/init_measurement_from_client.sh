root_path=/run/user/20001/data
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
    sudo nload -a 5 -u k nload -t 1000 -m devices c${client_id}-eth$i > ${measurement_result_path}nload/nload_log_${client_id}_${client_zone}_${i}.txt &
done
