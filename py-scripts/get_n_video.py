import subprocess
import json
import sys
import re
import numpy as np
import copy

# print(sys.argv[0])

server_id = int(sys.argv[1])
router_id = int(sys.argv[2])
measurement_result_path = str(sys.argv[3])


# machines=json.load(open("/home/mininet/machine.json"))
# clients=json.load(open("/home/mininet/hosts.json"))
# print("get_n_video")
# print("%siftop/iftop_log_%s.txt"%(str(measurement_result_path), str(server_id)))
fh = subprocess.Popen("tail -100 %siftop/iftop_log_%s.txt"%(str(measurement_result_path), str(server_id)), stdout=subprocess.PIPE, shell=True)
lines = reversed(fh.stdout.readlines())
# lines2 = copy.deepcopy(lines)
cnt = 0

ips = []
zones = []
speeds = {}
# print(clients)

lines2 = []
for raw_line in lines:
    line = raw_line.decode('ascii')
    # print(line)
    lines2.append(line)
    if line.startswith("=="):
        cnt += 1
# fh.kill()

# fh2 = subprocess.Popen("tail -100 /data/measurement_log/iftop/iftop_log_%s.txt"%(str(server_id)), stdout=subprocess.PIPE, shell=True, start_new_session=True)
# lines2 = reversed(fh2.stdout.readlines())
for line in lines2:
    # line = raw_line.decode('ascii')
    # print(line)
    if line.startswith("=="):
        cnt -= 1
    if cnt > 1:
        continue
    if cnt <= 0:
        break
    # print(cnt)
    # print(line)

    if "<=" in line:
        last_info = line.split("<=")[0].replace(" ", "")
        # print(line)
        # print(last_info)
    
    if "=>" in line:
        # print(line)
        speed = line.split("=>")[1].split("b")[2]
        # print(speed)
        if 'M' in speed:
            speed = float(speed.split('M')[0]) * 1000
        elif 'K' in speed:
            speed = float(speed.split('K')[0]) 
        else:
            speed = float(speed) / 1000
        ip_add = ''
        for item in last_info.split('.'):
            if item.isdigit():
                if ip_add:
                    ip_add = ip_add + '.' + item
                else:
                    ip_add = item

        if not re.search('10.0.*.1', ip_add):
            continue
        ip_id = int(ip_add.split('.')[2])
        if ip_id not in speeds:
            speeds[ip_id] = [speed]
        else:
            speeds[ip_id].append(speed)
        
        # if ip_add not in ips:
        #     ips.append(ip_add)
        # print(ip_add)
        # print(speed)

# print(ips)
# print(speeds)


# for client in clients:
#     if 'us-' in client['zone']:
#         zone = 'northamerica'
#     else:
#         zone = client['zone'].split('-')[0]
#     print(client, zone)

# ans=0
# for ip in ips:
#     # print(ip)
#     for client in clients:
#         if client['hostname'] == ip:
#             if 'us-' in client['zone']:
#                 zone = 'northamerica'
#             else:
#                 zone = client['zone'].split('-')[0]
#             ans = ans + float(geo_ratio[zone])
#             # print(client)
#             break
# print(ans)

if router_id in speeds.keys():
    print(np.mean(speeds[router_id]))
else:
    print(0)