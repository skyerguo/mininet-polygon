for i in `seq 0 5`
do
    ## nload记录文件为nload_log_ca_czb_sc，根据client的interface，记录的是client_a到server_c的实时流量，按照cz_b，也就是dispatcher_b聚类。
    ## 每3000毫秒记录一次，全部数据每100秒刷新一次以防文件过长，按照kBit/s记录结果

    ## 刷新间隔，稍微错开一点，防止nload同时跑起来
    refresh_interval=`awk 'BEGIN{print "3000" + ("50" * "'$i'")}'`
    echo "refresh_interval: " $refresh_interval
    echo sudo nload -a 100 -u k -t $refresh_interval -m devices c${client_id}-eth$i 
    
    # 错峰运行nload，防止I/O爆炸
    temp_time=$((${RANDOM=$i} % 1000)) 
    temp_time=`awk 'BEGIN{print "'$temp_time'" / "1000"}'`
    sleep $temp_time
done
