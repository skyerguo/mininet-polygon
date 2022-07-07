# import CpuUsage
import time
import threading
import requests
import base64
import os
import sys
import configparser
import subprocess


class FixLenList:
    def __init__(self, size):
        self.maxlen = size
        self.list = []
    def push(self,e):
        self.list.append(float(e))
        if(len(self.list) > self.maxlen):
            self.list.pop(0)
    def get(self):
        return self.list


class LoadMonitor(threading.Thread):
    def __init__(self, DNS_IP, serverID, next_layer_ip, this_layer_ip, threshold):
        threading.Thread.__init__(self) 
        self.DNS_IP = DNS_IP
        self.PORT = 12345
        self.serverID = serverID
        self.next_layer_ip = next_layer_ip
        self.this_layer_ip = this_layer_ip
        self.BEAT_PERIOD = 1
        self.last_server_ip = this_layer_ip
        self.threshold = float(threshold)
    
    def run(self):
        redis_ip = dns_ip

        count = 0
        size = 15
        flag_list = FixLenList(size)
        while True:
            count += 1
        
            ret = subprocess.Popen("redis-cli -h %s -a 'Hestia123456' get cpu_s%s_d%s"%(redis_ip,str(server_id),str(server_id)),shell=True,stdout=subprocess.PIPE)
            cpu_idle = ret.stdout.read().decode("utf-8").strip('\n')
            ret.stdout.close()

            try:
                cpu_idle = float(cpu_idle)
            except:
                ## redis没查到，认为是实验还买开始
                time.sleep(self.BEAT_PERIOD)
                continue
            
            # print("now_cpu_idle: ", cpu_idle)
            if cpu_idle < self.threshold:
                # print ('cpu usage: %d \t sum(flag_list.get()): %d'%(cpu_usage,sum(flag_list.get())))
                flag_list.push(1)
            else:
                flag_list.push(0)

            if sum(flag_list.get()) > 0.8 * size and self.last_server_ip != self.next_layer_ip:
                # res = requests.get("http://" + self.DNS_IP + ":12345/dns/" + str(self.serverID) + '_' + self.next_layer_ip)
                self.last_server_ip = self.next_layer_ip
                # print(res.content)

            if sum(flag_list.get()) < 0.3 * size and self.last_server_ip != self.this_layer_ip:
                # res = requests.get("http://" + self.DNS_IP + ":12345/dns/" + str(self.serverID) + '_' + self.this_layer_ip)
                self.last_server_ip = self.this_layer_ip
                # print(res.content)

            time.sleep(self.BEAT_PERIOD)


if __name__ == "__main__":  
    if len(sys.argv) < 2:
        print("pls provide the server id")
        exit(0)

    server_id = int(sys.argv[1])
    # print(server_id)

    threshold = 20 # 使用50%转发到下一层
    domain_id = server_id ## 一开始所有server都加到domain里，对应dns.py和start_client.sh
    # if server_id < 3: ## 修改的话，需要对应修改start_client.sh
    #     domain_id = 1
    # else:
    #     domain_id = 2
    if server_id in [3,7,14]: ## 最内层不转发
        # print(server_id)
        threshold = 100
    
    print('domain_id:\t', domain_id)
    print('threshold:\t', threshold)

    # print(111)

    config = configparser.ConfigParser()
    config.read('./ip.conf')
    dns_ip = config.get("DNS", "exter")
    print("DNS server's IP", dns_ip)
    this_layer_ip = config.get("server", "s"+str(server_id))
    print("This layer server's IP", this_layer_ip)

    # 监控心跳数据包
    if threshold != 100:
        next_layer_ip = config.get("server", config.get("layer", "s"+str(server_id)))
        print("Next layer server's IP", next_layer_ip)
        udp = LoadMonitor(dns_ip, 
                        serverID=str(domain_id), 
                        next_layer_ip=next_layer_ip, 
                        this_layer_ip=this_layer_ip,
                        threshold=threshold)
        udp.start() 
