while getopts ":i:" opt
do
    case $opt in
        i)
            server_id=$OPTARG
            hostname="server"$server_id
        ;;
    esac
done

tmux has-session -t $server_id 2> /dev/null; if [[ $? == 0  ]]; then tmux kill-session -t $server_id; fi
tmux new-session -ds $server_id
for i in `seq 4`
do
    tmux new-window -t $server_id:${i}
done

## TODO流量监控
tmux send-key -t $server_id:0 "sudo iftop -t > /data/measurement_log/iftop/iftop_log_$server_id.txt" Enter
