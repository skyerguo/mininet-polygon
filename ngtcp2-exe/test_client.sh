# sudo timeout 430 sudo LD_LIBRARY_PATH=${root} ${root}/client ${target_anycast} $port -i -p $data_type -o $opt -w $website --client_ip ${client_ip} --client_process ${port} --time_stamp ${time_stamp} -q 1>> /users/myzhou/client_tmp_${port}.log 2>> /users/myzhou/experiment_results/anycast_${unique_identifier}.log
sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 127.0.0.1 4433 -i -p normal_1 -o 1 -w google.com --client_ip 127.0.0.1 --client_process 4433 --time_stamp 1234567890 -q 

# LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 10.0.0.3 4443 -i -p normal_1 -o 1 -w google.com --client_ip 10.0.0.1 --client_process 4443 --time_stamp 1234567890 -q 

# sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/client 127.0.0.1 4443 -i -p normal_1 -o 1 -w google.com --client_ip 127.0.0.1 --client_process 4443 --time_stamp 1234567890 -q 