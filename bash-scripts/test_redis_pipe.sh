output_fake_throughput="/users/myzhou/fake_throughput.log"

fake_server_number=10000
dispatcher_id=0
redis_ip="198.22.255.15"
thread_number=100
for i in `seq $fake_server_number`
do
    temp=$((${RANDOM=$date} % 100 - 100)) ## -1 ~ -100随机一个数
    echo "set throughput_s${i}_d${dispatcher_id} $temp" >> $output_fake_throughput
done

todos $output_fake_throughput
tail -n $fake_server_number $output_fake_throughput | redis-cli -h $redis_ip -a 'Hestia123456' --pipe

for i in `seq $fake_server_number`
do
    temp=$((${RANDOM=$date} % 100 - 100)) ## -1 ~ -100随机一个数
    echo "get throughput_s${i}_d${dispatcher_id}" >> $output_fake_throughput
done

echo "fake_server_number: " $fake_server_number
for thread_id in `seq 0 $thread_number`
do
    {
        begin_time=$(date +%s%N)
        # echo "begin_time: "$begin_time "us"
        # output_fake_throughput="/proj/quic-PG0/data/measurement_log/2022-07-17_15:55:40/server/fake_throughput_s0_d0.log"
        todos $output_fake_throughput ## 转换成dos格式
        tail -n $fake_server_number $output_fake_throughput | redis-cli -h $redis_ip -a 'Hestia123456' --pipe
        end_time=$(date +%s%N)
        # echo "end_time: "$end_time "us"
        time_duratoin=$(($end_time - $begin_time))
        echo "thread_id: " $thread_id
        echo "time_duratoin: "$[$time_duratoin / 1000000] "ms"
    } &
done