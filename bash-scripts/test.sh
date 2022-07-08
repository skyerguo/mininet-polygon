
fake_server_number=10
for i in `seq $fake_server_number`
do
    temp_latency=$((${RANDOM=$date} % 100 - 100)) 
    echo $temp_latency
    echo $i
done