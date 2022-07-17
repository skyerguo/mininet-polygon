output_fake_throughput="/users/myzhou/fake_throughput.log"

fake_server_number=1000
dispatcher_id=0
redis_ip="198.22.255.15"
for i in `seq $fake_server_number`
do
    temp=$((${RANDOM=$date} % 100 - 100)) ## -1 ~ -100随机一个数
    echo "set throughput_s${i}_d${dispatcher_id} $temp" >> $output_fake_throughput
done

# output_fake_throughput="/proj/quic-PG0/data/measurement_log/2022-07-17_15:55:40/server/fake_throughput_s0_d0.log"
todos $output_fake_throughput ## 转换成dos格式
tail -n $fake_server_number $output_fake_throughput | redis-cli -h $redis_ip -a 'Hestia123456' --pipe
