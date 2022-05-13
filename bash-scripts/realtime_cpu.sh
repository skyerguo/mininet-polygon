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

# echo "machine_full: "${machine_type}${machine_name}
root_path='/sys/fs/cgroup/cpuacct/'${machine_type}${machine_name} ## mininet内的节点没有访问这个文件夹的权限。

cfs_us_limit=`cat $root_path/cpu.cfs_quota_us`
cfs_us_per_core=`cat $root_path/cpu.cfs_period_us` ## 每个核，xx us
limit_ratio=`awk 'BEGIN{print "'$cfs_us_limit'" / ("'$cfs_us_per_core'" * "64")}'` ## 每分母数微妙，能使用分子数微妙的cpu，最后得出一个百分比。
# echo "limit_ratio" $limit_ratio

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
    echo $usage_ratio
    # return $usage_ratio
elif [[ $monitor_type == "idle" ]]; then
    # return $idle_ratio
    echo $idle_ratio
else 
    echo "未知监控类型"
fi