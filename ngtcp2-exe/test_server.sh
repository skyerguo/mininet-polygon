# sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/server --interface=ens4 --unicast=${unicast} 0.0.0.0 $port /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt -q 1>> /users/myzhou/server_tmp_${port}.log 2>> /users/myzhou/server_${port}.log
sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/server --interface=eno1 --unicast=127.0.0.1 0.0.0.0 4433 /proj/quic-PG0/data/server.key --respath=/proj/quic-PG0/data/result-logs/dispatcher/2021-11-22_11:14:08/ /proj/quic-PG0/data/server.crt -q 
# sudo LD_LIBRARY_PATH=/proj/quic-PG0/data /proj/quic-PG0/data/server --interface=ens4 --unicast=127.0.0.1 0.0.0.0 4443 /proj/quic-PG0/data/server.key /proj/quic-PG0/data/server.crt -q 