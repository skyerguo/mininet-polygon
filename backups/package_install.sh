cd ${HOME}
sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCzVnXiSVFWYkzDM9FGqLvAOxNxwcl9uu21IgQxoaDnm/tnSdzMGyJ+qO+6wReu1gaJuoHDESjiDo/5wxQD9pd8pX8QI0m44DmUS6WvNCjCGoaGN50JOHGwHboRI58qQ8GL1N73fnkuKAuIkZ9sLit5uUKcNua7RIbiWtH4LqkcgxXvcz5+KUMQErBgt65t4yxN4RqCS488du/6pZneE5O74kxNtgwwpkIZYlEnORuFYWYOQnYb8TO/SqxyL60JQ06mQQESD8SpnoUgvdR3hW72TKRXq7LRxPHxEH+9oscprpY0IGowAl/suPNV4Rh0jpnuNqwnpIOUCNINBxexC4Mao8UNgY7NQ9UCyfmwX0W4Bnihp6WrNEBgo5L9dB9bU97QbsfL2qUvd3Ddnt0yFNkTB5ZXeU7a7UxzdZkH7rZbCkBgZU6GeU9MExXoYxpRx5kC5TfKQYpVQU2dYnqgSLVwzE/3Oo0Md350exfcC5yY0nlKsVC3+JxrDS9OogxndUM= aerber@qq.com" >> ~/.ssh/authorized_keys

sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -yqq unzip zip make gcc libncurses5-dev jq libev-dev iftop wondershaper

## install lexbor，暂时不需要了
# curl -O https://lexbor.com/keys/lexbor_signing.key
# sudo apt-key add lexbor_signing.key
# sudo chown mininet /etc/apt/sources.list.d/ -R
# sudo chgrp mininet /etc/apt/sources.list.d/ -R
# echo "deb https://packages.lexbor.com/ubuntu/ bionic liblexbor" >> /etc/apt/sources.list.d/lexbor.list
# echo "deb-src https://packages.lexbor.com/ubuntu/ bionic liblexbor" >> /etc/apt/sources.list.d/lexbor.list
# sudo apt-get update
# sudo DEBIAN_FRONTEND=noninteractive apt-get install -yqq liblexbor liblexbor-dev 

## install hiredis c++调用redis，暂时不需要了
# cd ~/ && wget https://github.com/redis/hiredis/archive/refs/heads/master.zip
# unzip master.zip
# mv hiredis-master hiredis && cd hiredis
# sudo make install && cd ~/
# sudo cp -r ~/hiredis /usr/local/lib
# sudo ldconfig /usr/local/lib

## install iptraf
if [ ! -d "${HOME}/iptraf-ng-1.2.1" ]; then
    wget https://github.com/iptraf-ng/iptraf-ng/archive/refs/tags/v1.2.1.zip
    unzip v1.2.1.zip
    cd iptraf-ng-1.2.1
    sudo make install
fi

## install iperf3
sudo apt -y remove iperf3 libiperf0 
sudo apt -y install libsctp1 
wget https://iperf.fr/download/ubuntu/libiperf0_3.7-3_amd64.deb 
wget https://iperf.fr/download/ubuntu/iperf3_3.7-3_amd64.deb 
sudo dpkg -i libiperf0_3.7-3_amd64.deb iperf3_3.7-3_amd64.deb

echo "finish dpkg"

# root=${HOME}"/polygon"
# script_path=${HOME}"/mininet-polygon"
# data_path=${root}"/experiment/init_machine"
# cd ${root}

##  数据传输，由于文件共享，暂时也不需要了
# [ -e data ] && rm -r data
# cp -r ${data_path}/server_data/. ${HOME}/data
# cp -r ${data_path}/client_data/. ${HOME}/data
# cp -r ~/data/websites ./
# mkdir -p ~/experiment_results

## 把server和client要装的包，都放在一起装了 
# envir
# bash ${HOME}/data/server_envir.sh
# bash ${HOME}/data/client_envir.sh
