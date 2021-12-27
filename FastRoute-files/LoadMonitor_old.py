import CpuUsage
import time
import threading
import requests
import base64
import os
import sys
import configparser


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
        cpuusage = CpuUsage.CpuUsage()

        count = 0
        size = 15
        flag_list = FixLenList(size)
        while True:
            count += 1
            cpu_usgae = cpuusage.getCpuUsage()
            if cpu_usgae > self.threshold:
                # print ('cpu usage: %d \t sum(flag_list.get()): %d'%(cpu_usgae,sum(flag_list.get())))
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
    # if len(sys.argv) < 3:
    #     print("pls provide the layer location of this server and threshold")
    #     exit(0)

    myhost = os.uname()[1]
    print('myhost:\t', myhost)
    server_id = myhost

    threshold = 50
    if server_id[-10] == '1' and server_id.split('-')[2] == 'southeast1':
        domain_id = 1
    if server_id[-10] == '1' and server_id.split('-')[2] != 'southeast1':
        domain_id = 2
    if server_id[-10] == '2':
        domain_id = 1
        threshold = 100
    print('domain_id:\t', domain_id)
    print('threshold:\t', threshold)

    config = configparser.ConfigParser()
    config.read('./ip.conf')
    dns_ip = config.get("DNS", "exter")
    print("DNS server's IP", dns_ip)
    this_layer_ip = config.get("server", server_id)
    print("This layer server's IP", this_layer_ip)

    # 监控心跳数据包
    if threshold != 100:
        next_layer_ip = config.get("server", config.get("layer", server_id))
        print("Next layer server's IP", next_layer_ip)
        udp = LoadMonitor(dns_ip, 
                        serverID=str(domain_id), 
                        next_layer_ip=next_layer_ip, 
                        this_layer_ip=this_layer_ip,
                        threshold=threshold)
        udp.start() 
