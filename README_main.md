[TOC]

# Mininet网络拓扑

## Mininet简介

​	Mininet是一种运行在单台机器上的SDN网络仿真环境。(https://github.com/mininet/mininet)

​	Mininet主要有几种部件：host，switch，controller，link。

		1. host可以认为是一台机器，可以当作一个ubuntu的机器，直接运行ubuntu的指令。它命令的作用域为这个host的本身。
		2. switch是交换机，它配置在Mininet内置的OVS switches平面上。它的作用域为整个OVS平面，可以操作所有的switch，也可以操作虚拟机。
		3. controller是控制器，可以接入远程的地址，可以通过controller向mininet内部输入命令，做到实时控制的效果。
		4. link是链路，上面可以配置一些所需的链路设置。两个host之间不能直接通过链路通信，需要至少经过一个switch进行信息交换。

​		

## 搭建

### 第一步：虚拟机的配置

​	我们使用Oracle VM VirtualBox创建了一个具有6核的CPU和10G内存的虚拟机，搭建我们的Mininet网络结构。

#### 配置网卡

​	在Settings-Network中，需要开启两个Adapter。

​	Adapter，设置Attached to “NAT”，这样才能保证，Mininet构建后，内部的switch能连外网。

​	Adapter，设置Attached to “Bridged Adapter”，Name选择“enp0s31f6”。这样Mininet构建后，内部网络能从dhcp获得一个ip，从而能远程ssh登陆。

#### 配置硬盘

​	首先在虚拟机创建足够大的盘

```
VBoxManage list hdds
VBoxManage modifyhd "/home/myzhou/VirtualBox VMs/Mininet-VM/mininet-vm-x86-64.vdi 3e57acdb-62e5-4f3a-bc9c-15a9892f08a6 --resize 40960
```

​	在Settgings-Storage里分配硬盘

​	进入mininet后，挂载上该硬盘

```
sudo vim /etc/fstab
在最后一行添加”/dev/sda3 /data ext4 defaults 0 0“，然后:wq退出保存
这样在/data，就能有个40G的硬盘了
```

#### 配置CPU核数

​	在Settings-Processor-Processors(s)里，通过拖动滑块，给mininet的虚拟机分配核数

### 第二步：虚拟机的安装（有镜像跳过）

#### 设置时区

```
cd ${HOME}
sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```



#### 安装mongodb

```

$ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 4B7C549A058F8B6B
$ echo "deb [ arch=amd64 ] https://mirrors.tuna.tsinghua.edu.cn/mongodb/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
$ sudo apt-get update
$ sudo apt-get install -y mongodb-org
$ sudo systemctl enable mongod
$ sudo service mongod restart
$ sudo apt-get install -y python3-pymongo
```

#### 安装redis

##### 安装hiredis

```
$ cd ~
$ git clone https://github.com/redis/hiredis
$ cd hiredis
$ make
$ sudo make install
$ sudo cp -r ~/hiredis /usr/local/lib
$ sudo ldconfig /usr/local/lib
```

##### 安装redis-server

```
$ sudo apt-get -y install redis-server
$ sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf
$ sudo sed -i 's/# requirepass foobared/requirepass Hestia123456/g' /etc/redis/redis.conf
$ sudo service redis-server restart
```

#### 配置语言环境

```
echo "export LC_ALL=C" >> ~/.zshrc 
source ~/.zshrc
```

#### 安装git，并导入仓库

```
$ sudo apt-get update
$ sudo apt-get -y install git
$ git clone git@github.com:skyerguo/Hestia.git
$ cd ~/ngtcp2
$ git checkout -b resource-demand
$ git branch --set-upstream-to=origin/resource-demand resource-demand
$ git clone git@github.com:skyerguo/mininet-polygon.git
$ cd ~/mininet-polygon
$ git checkout -b csd_version
$ git branch --set-upstream-to=origin/csd-version csd-version
```

#### 编译ngtcp2

##### 安装需要的包

```
$ sudo apt-get install -yqq pkg-config autoconf automake autotools-dev libtool libev-dev gdb zip unzip libcunit1 libcunit1-doc libcunit1-dev
$ sudo DEBIAN_FRONTEND=noninteractive apt-get install -yqq unzip zip make gcc libncurses5-dev jq libev-dev iftop wondershaper
$ cd ~
$ curl -O https://lexbor.com/keys/lexbor_signing.key
$ sudo apt-key add lexbor_signing.key
$ sudo chown gtc /etc/apt/sources.list.d/ -R
$ sudo chgrp gtc /etc/apt/sources.list.d/ -R
$ echo "deb https://packages.lexbor.com/ubuntu/ bionic liblexbor" > /etc/apt/sources.list.d/lexbor.list
$ echo "deb-src https://packages.lexbor.com/ubuntu/ bionic liblexbor" >> /etc/apt/sources.list.d/lexbor.list
$ sudo apt-get update
$ sudo apt-get install -yqq liblexbor liblexbor-dev
```

##### 配置openssl

 ```
$ cd ~/
$ git clone --depth 1 -b quic https://github.com/tatsuhiro-t/openssl
$ cd openssl
$ ./config enable-tls1_3 --prefix=$PWD/build
$ make -j$(nproc) && make install_sw
 ```

##### 配置ngtcp2

```
$ cd ~/ngtcp2
$ autoreconf -i
$ ./configure.sh && make
```

##### 移动可执行文件

```
$ cd ~/ngtcp2
$ cp examples/server /data/server
$ cp examples/dispatcher /data/dispatcher
$ cp examples/client /data/clent
¥ cp -r ~/openssl /data/
```

#### 安装iperf3

```
sudo apt -y remove iperf3 libiperf0 
sudo apt -y install libsctp1 
wget https://iperf.fr/download/ubuntu/libiperf0_3.7-3_amd64.deb 
wget https://iperf.fr/download/ubuntu/iperf3_3.7-3_amd64.deb 
sudo dpkg -i libiperf0_3.7-3_amd64.deb iperf3_3.7-3_amd64.deb
```



### 第三步：虚拟机的初始化

#### 初始化mongodb

​	由于mininet内部的host不能通过访问127.0.0.1访问mongo，只能通过mininet虚拟机的外网IP地址（ssh能连通的IP地址访问），且不能使用27017端口。后统一改为27117端口。

​	该初始化文件在执行main.py函数，会自动运行

#### 初始化redis

​	由于service 启动redis-server可能存在问题，可以用手动的方式启动redis-server

```
$ sudo /usr/bin/redis-server /etc/redis/redis.conf
```

​	如何测试redis-server启动成功

```
 $ redis-cli -a Hestia123456 ping
```

​	如果返回一行“PONG”，则redis-server启动成功

#### 清空mininet旧有的配置信息

本步骤在每次实验结束后进行一次，否则上一次实验如果没有完全关闭mininet，会导致一些错误。

```
$ sudo mn -c
```



### 第四步：添加数据（有镜像跳过）

#### 添加websites

在/data/websites下，分别存放cpu, normal_1和video三个文件夹，请求的文件都将从这里获取

``` 
$ cp -r ~/mininet-polygon/data_prepare/websites /data/websites
```



#### 添加mongodb数据

首先执行

```
$ python3 ~/mininet-polygon/data_prepare/insert_shuffle.py
```

数据添加到mongo的shuffle_index数据库里，shuffle_100w的表格。



## 构建拓扑

#### 修改拓扑文件

文件位置：~/mininet-polygon/py-scripts/topo.py

格式：

```
Middleware_client_dispatcher_server_test = { # 拓扑名称
		'client_number': 2, # client的数量
    'server_number': 2, # server的数量
    'dispatcher_number': 2, # dispatcher的数量
    'server_thread': 1, # server的并行端口数 
    'client_thread': 1, # client的并行端口数
    'dispatcher_thread': 1, # dispatcher的并行端口数
    'bw': { # 单位为Mbits/sec
        'client_server': [ # 表示第0个client和第0个，第1个server之间的带宽
            [5,2],
            [2,5]
        ],
        'client_dispatcher': [
            [5,2],
            [2,5]
        ],
        'dispatcher_server': [
            [10,3],
            [3,10]
        ],
    },
    'delay': { # 这里的记录的是rtt的值，实际的图中单向的delay为这里数值的一半，单位为ms
        'client_server': [
            [30,300], # 表示第0个client和第0个，第1个server之间的延迟
            [300,30]
        ],
        'client_dispatcher': [
            [20,200], # 实际上，这里设置为client和server延迟的2/3
            [200,20]
        ],
        'dispatcher_server': [
            [10,100], # 实际上，这里设置为client和server延迟的1/3
            [100,10]
        ],
    },
    'cpu': {
        'client': .2, # 表示所有client使用的cpu总量
        'server': .4,
        'dispatcher': .3,
    },
}
```

#### 应用修改后的拓扑

文件位置：~/mininet-polygon/py-scripts/main.py

修改“SELECT_TOPO = copy.deepcopy()”括号里，为上面的拓扑名称

#### 拓扑数据来源

1. delay： 通过测量谷歌云不同地区机器的ping值，设定client_server的delay。设定client_dispatcher为client_server的2/3，dispatcher_server为client_server的1/3。
2. bw：通过iperf3，测量谷歌云不同地区机器的带宽。假设最大带宽为5Mbits/sec，用此作为上线，等比例配置所有client_server的bw。设定client_dispatcher均为5Mbits/sec，dispatcher_server和client_server保持一致。
3. cpu：主要是server需要较高的cpu。
4. 具体谷歌云测量数据，可见“~/mininet-polygon/data_prepare/5*5demo.xlsx”

## 常用命令

```
net 显示网络链接情况
nodes 查看节点
dump 各个节点的信息
pingall
sh xxx 运行外部shell命令（从全局视角）
cx xxx 在host名为cx机器上，运行xxx指令
iperf h1 h2 两个hosts，h1和h2之间进行简单的iperfTCP测试
iperfudp h1 h2 两个hosts，h1和h2之间用制定带宽udp进行测试
```



# 代码说明

## 代码文件

```
mininet-polygon                                                         
├─ backups # 用来存储暂时没用的备份文件                                                                                       
├─ bash-scripts # 执行的bash脚本                                                        
│  ├─ init_measurement_from_server.sh # 测量初始化                                   
│  ├─ init_mongodb.sh # mongodb初始化                                                                                                     
│  ├─ measurement_from_server.sh # 在每个server调用此脚本，开始测量                                         
│  ├─ measurement_record.sh # 记录每秒redis数据库里记录的测量结果，用来结果展示                                                                                         
├─ data_prepare # 需要的数据准备                                                        
│  ├─ websites # 用来传输的websites                                                         
│  │  ├─ cpu # cpu资源，对应cpu sensitive                                                           
│  │  │  ├─ cpu                                                                                                 
│  │  ├─ normal_1 # normal_1资源，对应delay sensitive                                                      
│  │  │  └─ google.com                                                                                
│  │  └─ video # video资源，对应bandwidth sensitive                                                         
│  │     ├─ downloading # 5MB的文件
│  │     └─ downloadingcross # 1MB的文件                                                                                      
│  └─ insert_shuffle.py # 用来插入mongodb数据库的脚本                                                
├─ json-files # 存储Minient机器的json脚本                                                          
│  ├─ machine_client.json                                               
│  ├─ machine_dispatcher.json                                           
│  └─ machine_server.json                                               
├─ ngtcp2-exe # 用来运行的ngtcp文件                                                         
│  ├─ client                                                           
│  ├─ server                                                            
│  ├─ server.crt                                                        
│  ├─ server.key                                                        
│  ├─ start_client.sh # 启动实验的client                                                  
│  ├─ start_dispatcher.sh # 启动实验的dispatcher                                              
│  ├─ start_server.sh # 启动实验的server                                                  
│  └─ test_client.sh # 测试client能否在本机（非Mininet）跑起来
│  └─ test_dispatcher.sh # 测试dispatcher能否在本机跑起来 
│  └─ test_server.sh # 测试server能否在本机跑起来 
├─ py-scripts # 实验使用的python文件                                                                                                     
│  ├─ calc_success.py # 计算实验所有请求的成功率                                                  
│  ├─ get_n_video.py # 从iftop最后100行，实时分析每条链路的流量                                                   
│  ├─ get_std_data_DNS.py # 将DNS数据从原始数据导出到标准数据                                             
│  ├─ get_std_data_Polygon.py # 将Polygon数据从原始数据导出到标准数据                                           
│  ├─ main.py # 最主要的文件                                                          
│  └─ topo.py # Mininet拓扑配置信息                                                          
├─ README_main.md  # README主文档                                                                                                                
```

## 拓扑说明

为了实现设定网络，最终的拓扑结构如下：

### client

1. 所有client的IP地址为：10.0.x.1，其中x表示是第x个client，从0开始编号。
2. 每个client有SERVER_NUMBER(SN)+DISPATCHER_NUMBER(DN)个interface。前SN个interface名字为"cx-ethy"，表示这是第x个client，用来和第y个server边直连的interface；后DN个interface名字为“cx-ethz”，其中z=SN+w，表示这是第x个client，用来和第w个dispatcher边直连的interface。
3. 每个client的IP地址子网为/16。
4. 每个client的cpu能力为topo.py里设定的CPU能力，平均分给所有client

### server

1. 所有server的IP地址为：10.0.x.3，其中x表示是第x个server，从0开始编号。
2. 每个server有2个interface。第0个interface名字为"sx-eth0"，表示这是第x个server，用来和所有的client和dispatcher相连，获取数据；第1个interface名字为"sx-eth1"，表示这是第x个server，用来和mongodb、redis相连，可以连通外网。
3. 每个server的IP地址子网为/16。
4. 每个server的cpu能力为topo.py里设定的CPU能力，平均分给所有server

### dispatcher

1. 所有dispatcher的IP地址为：10.0.x.5，其中x表示是第x个dispatcher，从0开始编号。
2. 每个dispatcher有SN+2个interface。前SN个interface名字为"dx-ethy"，表示这是第x个dispatcher，用来和第y个server边直连的interface；第SN+1个interface名字为“dx-ethz”，其中z=SN，表示这是第x个dispatcher，用来和所有client相连的interface。第SN+2个interface名字为"dx-ethw"，其中w=SN+1，表示这是第x个dispatcher，用来和mongodb、redis相连，可以连通外网。
3. 每个dispatcher的IP地址子网为/16。
4. 每个dispatcher的cpu能力为topo.py里设定的CPU能力，平均分给所有dispatcher

### switch

1. switch的数量为SN+DN+1个。
   + 前SN个switch，主要用来服务所有server。switchx(0<=x<SN)首先连接网络接口"sx-eth0"，x表示第x个server。其次，它连接所有和serverx相连的client和dispatcher的网络接口。具体在[links](#links)中说明。
   + 接着DN个switch，主要用来服务所有dispatcher。switchy(y=SN+z, 0<=z<DN)首先连接网络接口"dz-ethw"(w=SN)，z表示第z个dispatcher。其次，它连接所有和dispatcherz相连的client的网络接口。具体在[links](#links)中说明。
   + 最后一个switch，用来和外网相连。

2. 所有switch需要允许IPv4的转发：“sysctl -w net.ipv4.ip_forward=1”
3. switch的路由详见[switch](#switch-routing)

### 网卡

​	eth0：第0号网卡，主要标记了本虚拟机的IP地址（通过ifconfig获取），可以在外网ssh连接，同时也能用来做数据库查询指定地址等操作。

​	eth1：第1号网卡，对应的是虚拟机启动配置的NAT Adapter，用来和某个switch（这里定义的是最后一个）相连，从而使得mininet内部节点可以通过连接最后一个switch，连入外网。每次实验前，需要用“ifconfig eth1 0”刷新eth1的配置。

### links

1. 有设定权重的边，即设定了如延迟、带宽等：
   + client-server：
     + “cx-ethy”连向“switchy”。表示这是第x个client，用来和第y个server边直连的interface。
   + dispatcher-server：
     + “dx-ethy”连向“switchz”。z=SN+y。表示这是第x个dispatcher，用来和第y个server边直连的interface；
   + client-dispatcher：
     + “cx-ethz”连向“switchw”。z=SN+y，w=SN+y。表示这是第x个client，用来和第y个dispatcher边直连的interface。
2. 没有设定权重的边：
   + 最后一个switch和所有的dispatcher，server相连。因为client不用访问外网，所有没有和client相连
   + switchx(0<=x<SN)和网络接口“sx-eth0”的边，x表示第x个server。
   + switchy(y=SN+z, 0<=z<DN)和网络接口"dz-ethw"(w=SN)的边，z表示第z个dispatcher。



## 路由说明

TODO

### client

### server

### dispatcher

### switch <span id = "switch-routing"></span>



## 运行说明

### 运行主文件

最后一位为方法，目前只提供["DNS", "Polygon"]两种

```
$ cd ~/mininet-polygon/py-scripts
$ sudo timeout 2000 python3 main.py DNS 
$ sudo timeout 2000 python3 main.py Polygon
```

建议在tmux中运行。

### 数据处理获取标准数据

最后一维的方法，和上面运行的主文件方法一致

```
$ cd ~/mininet-polygon/py-scripts
$ sudo python3 get_std_data_DNS.py
$ sudo python3 get_std_data_Polygon.py
```

每次数据处理的是，最后一次运行的主文件方法的时间戳。如果需要处理之前运行的数据，需要在代码中修改"start_time"字段，改为定死的时间戳。



# 数据说明

## 数据文件

### 原始数据

#### 测量数据

对于每组实验，记录一个开始时间戳st，格式为“年-月-日_时:分:秒” (举例而言，2021-11-28_11:56:26)。 每组实验的测量数据根目录为 “/data/measurement_log/${st}/”。

​      在每组实验测量数据的根目录下，分别有三个文件夹“iftop”，“server”和“record”。其中：

1．“server”文件夹记录了iftop命令的结果，用服务器的id进行区分。该数据用来计算实时的可获得带宽参数。举例而言，服务器3的iftop记录绝对路径为“/data/measurement_log/${st}/iftop/iftop_log_3.txt”；

2． “server”文件夹记录了cpu的测量情况，用服务器的id进行区分。cpu数据使用top命令以0.1秒的间隔记录。“server”文件夹同时记录了不同服务调度器在分析对该服务器测量数据的中间过程，包含了现有流量、cpu空闲率、剩余带宽等；

3．“record”文件夹记录了redis数据库的情况，用服务调度器的id进行区分。通过每秒对redis数据的访问，获取当前时刻所有服务器中redis中记录的三种资源的评分。

#### 实验数据

类似于测量数据，每组实验的实验数据也用同样的开始时间戳st标识。每组实验的实验数据根目录为“/data/result-logs/x/${st}”，其中x为client或server或dispatcher，分别表示从某种类型的机器上获取的数据。

​      对于client数据，每条请求记录一个该请求的时间tc。每条请求包含三个文件，分别为“{client_id}\_\{client_port}\_{tc}\_{type}.txt”。其中type为1表示标准输出，type为2表示用来记录结果的输出，type为tmp表示运行该请求的相关参数信息。

​      对于server数据，由于服务器持续监听，因此无法像客户端一样记录请求的时间。server的数据格式为“{server_id}\_\{server_port}\_{type}.txt”。其中type为1表示标准输出，type为2表示用来记录结果的输出，type为tmp表示运行该服务器的相关参数信息。

​      对于dispatcher数据，由于服务调度器持续监听，格式类似服务器的数据。dispatcher的数据格式为“{dispatcherr_id}\_\{dispatcher_port}\_{type}.txt”。其中type为1表示标准输出，type为2表示用来记录结果的输出，type为tmp表示运行该服务调度器的相关参数信息。



### 标准数据

​      将上述测量数据和实验数据进行整合，为了更方便直观地进行原型机数据的展示。每组实验的实验数据也用同样的开始时间戳st标识。标准数据存储的根目录为“/data/saved_results/${st}/${mode}”，其中mode为DNS表示这是一组DNS的实验数据，mode为Polygon表示这是一组Polygon的实验数据。

​      对于两种mode，均存储了以下文件夹和文件。

1．文件夹“{client_ip}\_jct”存储了该客户端的jct数据结果。文件夹下，每个文件为“{client_ip}\_{client_port}.txt”。文件中，每行由三个字符串，以空格分割。第一个字符串表示该请求的时间，第二个字符串表示请求的类型，第三个字符串表示jct的时间（单位为1E-6秒）。

2．文件夹“{dispatcher_ip}\_bw”存储了该服务调度器对n个服务器测量的bw指标结果。文件夹下，有一个“bw.txt”的文件。文件中，每行由若干个字符串组成，以空格分割。第一个字符串表示测量的时间，接下来n个字符串，分别表示该服务调度器到对应的服务器的可获得带宽指标（指标为[0,10000]的小数）。

3．文件夹“{dispatcher_ip}\_cpu”存储了该服务调度器对n个服务器测量的cpu指标结果。文件夹下，有一个“cpu.txt”的文件。文件中，每行由若干个字符串组成，以空格分割。第一个字符串表示测量的时间，接下来n个字符串，分别表示该服务调度器到对应的服务器的cpu空闲率指标（指标为[0,100]的小数）。

对于mode为Polygon的实验，还额外存储了以下文件夹和文件。

1．文件夹“{dispatcher_ip}\_routing”存储了该服务调度器的DRA算法选择逻辑以及选择的结果。文件夹下，有一个“routing.txt”的文件。文件中，每行由五个字符串，以空格分割。第一个字符串表示接受到请求的时间，第二个字符串表示发出请求的客户端的IP地址，第三个字符串为请求的敏感资源的类型，第四个字符串为routing_type，第五个字符串为响应请求的服务器的IP地址。其中routing_type为local表示转发给本区域的服务器，routing_type为forward表示转发给其他地区更优的服务器。

​      

## 数据处理

​	数据处理（从原始数据->标准数据）去除了一下几类数据

	1. plt为0的所有数据
	1. sensitive_type=cpu，但是cpu查询时间为显示的所有数据（即没有成功进行数据库查询）
	1. plt数量不为两个的文件（因为现在的websites，每个文件返回都应该是两个plt。如果只返回一个，说明只成功了握手，数据传输没有成功）



# 可能存在问题

## CPU测量

### 目前版本

位于~/mininet-polygon/bash-scripts/measurement_from_server.sh

```
server_pid=`ps aux | grep mininet:s${server_id} | grep -v grep | awk '{print $2}'`
top -p $server_pid -b -d 0.1 | grep -a '%Cpu' >> "${measurement_result_path}server/cpu_$server_id.log" & 
```

### 可能存在的问题

测量的cpu idle，不一定是Mininet的host对应的server实际可用的cpu。比如调用redis的cpu，就没有被统计到。

需要进一步理解，Mininet中CPULimitedHost的限制CPU逻辑，该如何更精确地测量一个host所剩余的CPU资源。

## server监听多个interface

### 目前版本

位于~/ngtcp2/examples/server.cc，在函数：

```
void create_sock(std::vector<int> *fds, const char *interface, const int port, int family, Server &s) 
```

绑定interface，目前只绑定sx-eth0。

### 可能存在的问题

以前的版本，可以同时监听两个interface，一个是从client来的interface，一个是从dispatcher来的interface "bridge"。

在mininet中，之前尝试过一种拓扑，使得server有两个interface，分别连接client和dispatcher，但是它无法监听从dispatcher来的interface的数据，未解决。

为了赶ddl，最后的拓扑将client和dispatcher的链路同时连到一个switch上，该switch再转给server，使得server只需要监听一个interface。

## server 运行cpu并写入时间

### 目前版本

​	使用“util::getUniqueLogFile”， 获得client存储的结果文件，并调用nohup python3将cpu调用mongodb查询的结果写入。

### 可能存在的问题

​	~/ngtcp2/examples/util.cc中的getUniqueLogFile函数，获取client_id的方法简单粗暴，直接看倒数第四位的数值了。

​	当client数量大于等于10的时候，需要修改~/ngtcp2/examples/util.cc里的对应逻辑。

## dispatcher中对于不同sensitive的敏感度排序

### 目前版本

​	sensitive_type目前按照1:0:0来，在代码“~/ngtcp2/examples/client.cc”中，使用98,1,1来表示。这是因为目前版本的ngtcp2，不允许添加sensitive参数为0的数据，会报错。

### 可能存在的问题

​	之后修改“~/ngtcp2/examples/client.cc”中不同资源的sensitive权重，需要注意0的问题。

​	“~/ngtcp2/examples/client.cc”中，对于权重加权排序，目前是只考虑收到98,1,1的情况并硬解码为1,0,0，需要修改这块解码逻辑，同时权重加权排序待检验。

​	

# 遇到的坑点

## mininet内的节点连接数据库

### redis

​	redis数据库无法在每个host节点内创建，只能采用统一的，建立在虚拟机上的redis。

​	redis-server数据库运行“service方法”总报错，采用“$ sudo /usr/bin/redis-server /etc/redis/redis.conf”手动运行

​	每台host的redis-cli，需要指定虚拟机上的IP地址。要保证host能连接上虚拟机上的IP地址。（详见下述[Mininet的节点连接外网](#Mininet的节点连接外网)）

### mongo

​	mongo的27017端口，无法通过Mininet访问。需要将端口改为27117。和redis一致，每台host访问mongodb时，需要指定使用虚拟机上的IP地址。

​	在main.py里，有每次重制mongod的操作，此操作是必须的，否则会导致mongodb有些情况下出现数据库错误问题，访问不到。

​	目前在~/mininet-polygon/data_prepare/websites/cpu/cpu/www.cpu/src/cpu.py（调用cpu sensitive的mongodb请求的文件）里，写死了host的ip地址，因为cpu.py里调用的太多了，如果每次都用ifconfig调用，代价消耗较大。



## Mininet的节点连接外网

### switch网关

TODO

10.0.2写死了

### 多个网卡

TODO



## Mininet如何配置网络拓扑

### TCLink

net.addLInk(x,y,cls=TCLink, **{'bw':bw['client_dispatcher'][client_id][dispatcher_id],'delay':str(int(delay['client_dispatcher'][client_id][dispatcher_id] / 2))+'ms', 'max_queue_size':1000, 'loss':0, 'use_htb':True})

请用**{json}的方式添加。

+ bw表示带宽，单位为"Mbits/sec"

+ delay表示单向延迟，需要手动添加ms
+ max_queue_size为最大排队数
+ loss表示丢包率
+ use_htb：表示使用htb调度策略

### CPULimitedHost

在创建net的时候，设置所有的host都为CPU限制型的“host=CPULimitedHost,”。

在实际建立节点addHost时，每个点cpu=t，t为一个小数，表示占据整个虚拟机cpu能力的百分比。



### 边应该建立在哪里

不能在switch之间建立边，因为switch之间本来就能连通。最后的拓扑可能会乱走，导致switch之间的通路和设定的不同。

边应该建立在switch和host之间，再通过配置host的路由表，使得流量能按照预设的网络拓扑来。

### 网络路由表

千万不要用dhclient，容易直接卡死时间超久；或者获取结果失败且不报log。



### interface起名

由于mininet对于interface名字不能太长，比如dispatcher0-eth0就超过了限定会出奇怪的错误（且不会报错），所以需要将interface名字改短一点。

最后用第一个字母简化，比如用d0-eth0，代替dispatcher0-eth0。



### 创建时间

Mininet创建后，由于我们配置了大量的TCLink和CPULiminitedHost，还有许多switch。因此需要一定的等待时间等网络创建完成，否则运行后面的测量+实验会出现奇怪的问题，比如某条链路没通。

经过测试，等待时间至少为30秒。



## Mininet权限管理

### hosts

​	每个host可以管理自己内部的权限。包括interface，路由表等。

​	假设host h1，使用h1 xxx调用指令后，无法在xxx指令指定别的host或者sh的视角。

### sh

​	相当于在虚拟机执行bash命令。

### switches

​	所有的switch部署在OVS平面上，都可以获得所有switches的权限。和sh权限范围一致。

​	ovs-vsctl只能运用在统一的OVS平面上，而无法针对每个hosts进行配置。



## ngtcp2 GRE/socket

TODO

### 学兵关于GRE的逻辑

### 如何改为socket远程的sendto





## ngtcp2老版本存在的问题

### http使用的是我们自定义的lexbor

### 多并发出现Error

### 没有重传机制

### transport_parameters的修改

​	需要手动修改很多库文件。要保证加解密的位数正确。
