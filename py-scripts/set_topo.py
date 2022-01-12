import os
import csv

SET_MAX_BW = 5 ## 假设最大的带宽为5MB/s

csv_file_path = '../data-prepare/measure.csv'
f_in = open(csv_file_path, 'r')
csv_reader = csv.reader(f_in)

zone_number = 0
zone_map = {}

max_bw = 0

for line in csv_reader:
    area = line[0][:-2]
    if area not in zone_map:    
        zone_map[area] = zone_number
        zone_number += 1
        print(area)

    area = line[1][7:-2]
    if area not in zone_map:    
        zone_map[area] = zone_number
        zone_number += 1
        print(area)

    # # print(line[3])
    # if 'Mb' in line[3].split('_')[1]:
    #     max_bw = max(max_bw, float(line[3].split('_')[0]))
    # elif 'Gb' in line[3].split('_')[1]:
    #     max_bw = max(max_bw, float(line[3].split('_')[0]) * 1000)
    # elif 'Kb' in line[3].split('_')[1]:
    #     max_bw = max(max_bw, float(line[3].split('_')[0]) / 1000)

# latency_topo = [[0 for _ in range(zone_number)] for _ in range(zone_number)]
# bandwidth_topo = [['' for _ in range(zone_number)] for _ in range(zone_number)]

# for line in csv_reader:
#     src = zone_map[line[0][:-2]]
#     des = zone_map[line[1][7:-2]]

#     latency_topo[src][des] = float(line[2])
#     latency_topo[des][src] = float(line[2])

# # print(zone_number) 