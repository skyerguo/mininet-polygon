[TOC]

# Mininet网络拓扑

## Mininet简介

​	Mininet是一种运行在单台机器上的SDN网络仿真环境。(https://github.com/mininet/mininet)

​	Mininet主要有几种部件：host，switch，controller，link。

		1. host可以认为是一台机器，可以当作一个ubuntu的机器，直接运行ubuntu的指令。它命令的作用域为这个host的本身。
		1. switch是交换机，它配置在Mininet内置的OVS switches平面上。它的作用域为整个OVS平面，可以操作所有的switch，也可以操作虚拟机。
		1. controller是控制器，可以接入远程的地址，可以通过controller向mininet内部输入命令，做到实时控制的效果。
		1. link是链路，上面可以配置一些所需的链路设置。两个host之间不能直接通过链路通信，需要至少经过一个switch进行信息交换。

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

#### #### 配置语言环境

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
$ sudo DEBIAN_FRONTEND=noninteractive apt-get install -yqq unzip zip make gcc libncurses5-dev jq libev-dev iftop
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

#### 添加mongodb数据

首先执行

```
python3 /data/polygon/experiment/motivation/machine_preparation/insert_shuffle.py
```

数据添加到mongo的shuffle_index数据库里，shuffle_100w的表格。



## 构建拓扑

#### 首先修改拓扑文件

文件位置：~/mininet-polygon/py-scripts/topo.py

格式：





# 代码说明

## 代码文件

## 拓扑配置

## 运行说明





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



# 可能存在问题，待解决的坑点

## CPU测量

## server监听多个interface
