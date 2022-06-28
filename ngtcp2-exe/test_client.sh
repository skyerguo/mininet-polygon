# sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 198.22.255.11 4433 -i -p normal_1 -o 1 -w google.com --client_ip 127.0.0.1 --client_process 4433 --time_stamp 1234567890 -q &

nohup sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 198.22.255.11 4433 -i -p video -o 1 -w downloading --client_ip 127.0.0.1 --client_process 4433 --time_stamp 1234567890 -q 1>> ~/1_1.txt 2>> ~/1_2.txt &

sleep 3

nohup sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 198.22.255.11 4433 -i -p normal_1 -o 1 -w google.com --client_ip 127.0.0.1 --client_process 4433 --time_stamp 1234567890 -q 1>> ~/2_1.txt 2>> ~/2_2.txt &


# for i in `seq 1`
# do
#     {
#         for round in `seq 3`
#         do
#             current_time=$(date "+%Y-%m-%d_%H:%M:%S")
#             echo $i"th current_time: "$current_time
#             # sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 198.22.255.11 4433 -i -p video -o 1 -w downloading --client_ip 127.0.0.1 --client_process 4433 --time_stamp 1234567890 -q 1>> ./temp_${i}_${round}_1.txt 2>> ./temp_${i}_${round}_2.txt
#             sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 198.22.255.11 4433 -i -p video -o 1 -w downloadinginit --client_ip 127.0.0.1 --client_process 4433 --time_stamp 1234567890 -q 1>> ./temp_${i}_${round}_1.txt 2>> ./temp_${i}_${round}_2.txt
#             # sleep 1
#         done
#     } &
# done