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

### 第二步：虚拟机的安装（无镜像）

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

```
$ cd ~
$ git clone https://github.com/redis/hiredis
$ cd hiredis
$ make
$ sudo make install
$ sudo cp -r ~/hiredis /usr/local/lib
$ sudo ldconfig /usr/local/lib
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



### 第三步：虚拟机的初始化

#### 初始化mongodb

#### 初始化redis

#### 清空mininet旧有的数据

```
$ sudo mn -cgit pu
```









## 构建拓扑

#### 首先修改拓扑文件

文件位置：~/mininet-polygon/py-scripts/topo.py

格式：





# 代码说明



# 数据文件说明
