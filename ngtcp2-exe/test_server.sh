# sudo LD_LIBRARY_PATH=~/data ~/data/server --interface=ens4 --unicast=${unicast} 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q 1>> /home/mininet/server_tmp_${port}.log 2>> /home/mininet/server_${port}.log
sudo LD_LIBRARY_PATH=/data /data/server --interface=ens4 --unicast=127.0.0.1 0.0.0.0 4433 /data/server.key /data/server.crt -q 
# sudo LD_LIBRARY_PATH=/data /data/server --interface=ens4 --unicast=127.0.0.1 0.0.0.0 4443 /data/server.key /data/server.crt -q 