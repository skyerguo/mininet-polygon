import subprocess
import json
# import os

machines=json.load(open("/home/mininet/machine.json"));
clients=json.load(open("/home/mininet/hosts.json"));
fh = subprocess.Popen("tail -150 /home/mininet/iftop_log.txt", stdout=subprocess.PIPE, shell=True)
lines = reversed(fh.stdout.readlines())
# print(lines)
cnt=0
geo_ratio={}
routers = [x for x in machines if "router" in x]

std_ratio = open("/home/mininet/initial_std.txt").readlines()
for i in range(len(routers)):
    geo_ratio[routers[i].split('-')[1]] = float(std_ratio[i])
# print(geo_ratio)
# print(routers)

ips = []
zones = []
# print(clients)

for raw_line in lines:
    line = raw_line.decode('ascii')
    # print(line)
    if line.startswith("=="):
        cnt += 1
    if cnt == 0:
        continue
    if cnt == 2:
        break

    if "<=" in line:
        last_info = line.split("<=")[0].replace(" ", "")
        # print(line)
        # print(last_info)
    
    if "=>" in line:
        speed = line.split("=>")[1].split("b")[2]
        # print(line)
        # print(speed)
        if 'M' in speed or ('K' in speed and float(speed.split('K')[0]) > 200):
            # print(last_info)
            ip_add = ''
            for item in last_info.split('.'):
                if item.isdigit():
                    if ip_add:
                        ip_add = item + '.' + ip_add
                    else:
                        ip_add = item
            if ip_add not in ips:
                ips.append(ip_add)
            # print(ip_add)
            # print(speed)

# print(ips)


# for client in clients:
#     if 'us-' in client['zone']:
#         zone = 'northamerica'
#     else:
#         zone = client['zone'].split('-')[0]
#     print(client, zone)

ans=0
for ip in ips:
    # print(ip)
    for client in clients:
        if client['hostname'] == ip:
            if 'us-' in client['zone']:
                zone = 'northamerica'
            else:
                zone = client['zone'].split('-')[0]
            ans = ans + float(geo_ratio[zone])
            # print(client)
            break
print(ans)