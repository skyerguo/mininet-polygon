#!/bin/bash
iperf3 -s -p 5200 -D >/dev/null 2>&1
iperf3 -s -p 5201 -D >/dev/null 2>&1
iperf3 -s -p 5202 -D >/dev/null 2>&1
iperf3 -s -p 5203 -D >/dev/null 2>&1
iperf3 -s -p 5204 -D >/dev/null 2>&1
iperf3 -s -p 5205 -D >/dev/null 2>&1
iperf3 -s -p 5206 -D >/dev/null 2>&1
iperf3 -s -p 5207 -D >/dev/null 2>&1
iperf3 -s -p 5208 -D >/dev/null 2>&1
iperf3 -s -p 5209 -D >/dev/null 2>&1

hostname=`hostname`
main_test_ip="`jq -r .EXTERNAL_IP /proj/quic-PG0/data/server_settings.json`"
main_hostname=`jq -r .HOSTNAME /proj/quic-PG0/data/server_settings.json`

dispatcher_ips=(`python3 -c 'import json; import os; machines=json.load(open("/users/myzhou/machine.json")); print(" ".join([machines[x]["internal_ip1"] for x in machines if "dispatcher" in x]));'`)
server_ips=(`python3 -c 'import json; import os; machines=json.load(open("/users/myzhou/machine.json")); print(" ".join([machines[x]["external_ip1"] for x in machines if "server" in x]));'`)
server_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/users/myzhou/machine.json")); print(" ".join([x for x in machines if "server" in x]));'`)
dispatcher_hostnames=(`python3 -c 'import json; import os; machines=json.load(open("/users/myzhou/machine.json")); print(" ".join([x for x in machines if "dispatcher" in x]));'`)


# ps -ef | grep "top -b -d 0.1" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# start_time=$(date "+%Y%m%d%H%M%S")
# echo "start_time:" $start_time > ~/cpu.log
# top -b -d 0.1 | grep -a '%Cpu' >> ~/cpu.log &

dispatcher_num=-1
for i in `seq 0 $((${#dispatcher_hostnames[*]} - 1))`
do
    echo ${server_ips[$i]}
    if [[ ${dispatcher_hostnames[$i]} == $hostname ]] 
    then
        dispatcher_num=$i
    fi
done

sleep 20
time_stamp=$(($(date +%s%N)/1000000))
for i in `seq 0 $((${#dispatcher_hostnames[*]} - 1))`
do
    server_num=$(($i+$dispatcher_num))
    # echo "server_num: " $server_num
    server_num=$(($server_num%5))
    echo "server_num: " $server_num
    server_ip=${server_ips[$server_num]}

    if [[ $i == $dispatcher_num ]]
    then
        website=downloading
    else
        website=downloadingcross
    fi

    rm /users/myzhou/speed_dispatcher_$server_num.txt
    echo sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client ${server_ip} 4433 -i -p video -o 1 -w $website --client_ip 123.123.123.123 --client_process 4433 --time_stamp $time_stamp -q
    sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client ${server_ip} 4433 -i -p video -o 1 -w $website --client_ip 123.123.123.123 --client_process 4433 --time_stamp $time_stamp -q 1>> /dev/null 2>> /users/myzhou/speed_dispatcher_$server_num.txt
    # sudo 
    PLT_num=`sudo tac /users/myzhou/speed_dispatcher_$server_num.txt | grep -c "PLT"`
    time_spend=`sudo tac /users/myzhou/speed_dispatcher_$server_num.txt | grep -a "PLT" |head -n 1| awk '{print $2}'`
    while [[ $time_spend == 0 || $PLT_num -ne 2 ]] 
    do
        sleep 10
        rm /users/myzhou/speed_dispatcher_$server_num.txt
        sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client ${server_ip} 4443 -i -p video -o 1 -w $website --client_ip 123.123.123.123 --client_process 4433 --time_stamp $time_stamp -q 1>> /dev/null 2>> /users/myzhou/speed_dispatcher_$server_num.txt
    done
    echo "time_spend: " $time_spend

    if [[ $website == "downloading" ]]
    then
        size=5000
    else
        size=942
    fi
    rate=`awk 'BEGIN{print "'$size'" / "'$time_spend'"  * "1000000"}'`
    # echo rate > /users/myzhou/initial_${dispatcher_num}_${server_num}.txt

    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null gtc@${server_ip} "echo $rate > /users/myzhou/initial_${dispatcher_num}.txt"
    # sleep
done

echo "dispatcher_num: " $dispatcher_num
echo "initial done"