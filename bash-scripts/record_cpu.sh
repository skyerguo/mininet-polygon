root_path=/proj/quic-PG0/data
measurement_result_path=$root_path/measurement_log/
while getopts ":n:m:t:i:a:" opt
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
        a)
            measurement_result_path=${measurement_result_path}$OPTARG'/'
            mkdir -p $measurement_result_path
            mkdir -p ${measurement_result_path}"server"
        ;;

        ?)
            echo "未知参数"
            exit 1
        ;;
    esac
done

output_file=$measurement_result_path"server/"${machine_type}${machine_name}"_cpu.log"

root_path='/sys/fs/cgroup/cpuacct/'${machine_type}${machine_name}

while true; do 
    echo "current_time: "$(date "+%Y%m%d%H%M%S") >> $output_file

    if [ ! -f $root_path ]; then ## 路径不存在，即当mininet被关闭后自动结束该进程
        echo "Path not exists"
        break
    fi

    cfs_us_limit=`cat $root_path/cpu.cfs_quota_us`
    cfs_us_per_core=`cat $root_path/cpu.cfs_period_us` ## 每个核，xx us

    limit_us_per_monitor_interval=`awk 'BEGIN{print "'$monitor_interval'" * "1000000" / "'$cfs_us_per_core'" * "'$cfs_us_limit'"}'` ## 每monitor_interval秒能用多少微秒的cpu
    # echo "limit_us_per_monitor_interval" $limit_us_per_monitor_interval

    raw_usage_1=`cat $root_path/cpuacct.usage`
    # echo "raw_usage_1" $raw_usage_1

    sleep $monitor_interval

    raw_usage_2=`cat $root_path/cpuacct.usage`
    # echo "raw_usage_2" $raw_usage_2

    usage_diff=`awk 'BEGIN{print ("'$raw_usage_2'" - "'$raw_usage_1'") / "1000"}'` ## 单位是纳秒，注意单位转换为微秒
    # echo "usage_diff" $usage_diff

    # echo `awk 'BEGIN{print "'$usage_diff'" / "1000000" / "64"}'`
    usage_ratio=`awk 'BEGIN{print "'$usage_diff'" / "'$limit_us_per_monitor_interval'"}'`
    idle_ratio=`awk 'BEGIN{print "1" - "'$usage_ratio'"}'`

    # echo "usage_ratio" $usage_ratio
    # echo "idle_ratio" $idle_ratio

    if [[ $monitor_type == "usage" ]]; then
        echo "cpu_usage_ratio: " $usage_ratio >> $output_file

        # return $usage_ratio
    elif [[ $monitor_type == "idle" ]]; then
        # return $idle_ratio
        echo "cpu_idle_ratio: " $idle_ratio >> $output_file
    else 
        echo "未知监控类型"
    fi
done