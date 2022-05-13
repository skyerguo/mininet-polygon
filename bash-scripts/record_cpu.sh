while getopts ":n:m:t:i:" opt
do
    case $opt in
        n)
            machine_name=$OPTARG ## Mininet内的机器名称
        ;;
        m)
            machine_type=$OPTARG ## Mininet的机器前缀
        ;;
        t)
            monitor_type=$OPTARG ## 是要usage还是idle
        ;;
        i)
            monitor_interval=$OPTARG ## 两次监测的间隔时间
        ;;

        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

while true; do 
    
done