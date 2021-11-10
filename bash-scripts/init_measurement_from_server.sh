root_path=/data
measurement_result_path=$root_path/measurement_log/

while getopts ":i:a:" opt
do
    case $opt in
        i)
            server_id=$OPTARG
            hostname="server"$server_id
        ;;
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/'
            mkdir -p $measurement_result_path
            mkdir -p ${measurement_result_path}"iftop"
        ;;
    esac
done

# tmux has-session -t $server_id 2> /dev/null; 
# if [[ $? == 0  ]]; then tmux kill-session -t $server_id; fi
# tmux new-session -ds $server_id
# for i in `seq 4`
# do
#     tmux new-window -t $server_id:${i}
# done

# tmux send-key -t $server_id:0 "s0 sudo iftop -t > ${measurement_result_path}iftop/iftop_log_$server_id.txt" Enter

# tmux send-key -t $server_id:0 "iftop -t > ${measurement_result_path}iftop/iftop_log_$server_id.txt" Enter 
# nohup sudo iftop -t > ${measurement_result_path}iftop/iftop_log_$server_id.txt >${measurement_result_path}iftop/iftop_error_$server_id.txt 2>&1 &
sudo iftop -t > ${measurement_result_path}iftop/iftop_log_$server_id.txt &
