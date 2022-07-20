redis-cli -a Hestia123456 -n 0 flushdb
output_fake_throughput="/users/myzhou/fake_throughput.log"
rm $output_fake_throughput

fake_server_number=10000
dispatcher_id=0
redis_ip="198.22.255.15"
thread_number=1
for i in `seq $fake_server_number`
do
    temp=$((${RANDOM=$date} % 100 - 100)) ## -1 ~ -100随机一个数
    echo "set throughput_s${i}_d${dispatcher_id} $temp" >> $output_fake_throughput
done

todos $output_fake_throughput
cat $output_fake_throughput | redis-cli -h $redis_ip -a 'Hestia123456' --pipe

rm $output_fake_throughput
for i in `seq $fake_server_number`
do
    temp=$((${RANDOM=$date} % 100 - 100)) ## -1 ~ -100随机一个数
    echo "get throughput_s${i}_d${dispatcher_id}" >> $output_fake_throughput
done

total_begin_time=$(date +%s%N)
echo "fake_server_number: " $fake_server_number
output_fake_temp="/users/myzhou/fake_temp.log"
rm $output_fake_temp
for thread_id in `seq 0 $thread_number`
do
    {
        begin_time=$(date +%s%N)
        # echo "begin_time: "$begin_time "us"
        # output_fake_throughput="/proj/quic-PG0/data/measurement_log/2022-07-17_15:55:40/server/fake_throughput_s0_d0.log"
        todos $output_fake_throughput ## 转换成dos格式
        cat $output_fake_throughput | redis-cli -h $redis_ip -a 'Hestia123456' --pipe >> /dev/null
        end_time=$(date +%s%N)
        # echo "end_time: "$end_time "us"
        time_duration=$(($end_time - $begin_time))
        # echo "thread_id: " $thread_id
        # echo "time_duration: "$[$time_duratoin / 1000000] "ms"
        # sum_time=$(($sum_time + $time_duration))
        echo $time_duration >> $output_fake_temp
    } &
done
wait
# todos $output_fake_throughput ## 转换成dos格式
# begin_time=$(date +%s%N)
# cat $output_fake_throughput | redis-cli -h $redis_ip -a 'Hestia123456' --pipe >> /dev/null
# end_time=$(date +%s%N)
# time_duration=$(($end_time - $begin_time))
# echo $time_duration >> $output_fake_temp

sum_time=0
while read rows
do
    # echo "Line contents are : $rows "
    sum_time=$(($sum_time + $rows))
    # echo $sum_time
done < $output_fake_temp

sum_time=$[$sum_time / 1000000]
# echo "sum_time: "$sum_time

# total_end_time=$(date +%s%N)
# total_time_duration=$[$(($total_end_time - $total_begin_time)) / 1000000]
# echo "total_time_duration: "$total_time_duration
avg_time_duration=`awk 'BEGIN{print "'$sum_time'" / "'$thread_number'"}'`
echo "avg_time_duration: "$avg_time_duration "ms"