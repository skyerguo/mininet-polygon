import os
import numpy as np

root_path = [_ for _ in range(5)]
root_path[0] = "/proj/quic-PG0/data/result-logs/dispatcher/2022-07-17_21:28:55/0/" ## 100
root_path[1] = "/proj/quic-PG0/data/result-logs/dispatcher/2022-07-17_20:58:05/0/" ## 1000
root_path[2] = "/proj/quic-PG0/data/result-logs/dispatcher/2022-07-17_21:47:01/0/" ## 10000
root_path[3] = "/proj/quic-PG0/data/result-logs/dispatcher/2022-07-17_22:04:21/0/" ## 20000
root_path[4] = "/proj/quic-PG0/data/result-logs/dispatcher/2022-07-17_22:21:42/0/" ## 120000

for i in range(5): 
    files = os.listdir(root_path[i])
    files.sort(reverse=True)

    times_all = {
        'parse': [], ## 读取quic包
        'redis': [], ## 查询redis
        'sort': [], ## 排序
        'forward': [], ## 转发
    }

    for file_name in files:
        if "_2" not in file_name:
            continue
        f_in = open(root_path[i] + file_name)
        for line in f_in:
            if "Parsing QUIC packet costs" in line:
                times_all['parse'].append(float(line.split(' ')[-2]))
            elif "Executing redis costs" in line:
                times_all['redis'].append(float(line.split(' ')[-2]))
            elif "Sort weighted_servers costs" in line:
                times_all['sort'].append(float(line.split(' ')[-2]))
            elif "Forward total costs" in line:
                times_all['forward'].append(float(line.split(' ')[-2]))
        # print(file_name)
        f_in.close()
    print("id: ", i)

    for key in times_all:
        print(key, np.mean(times_all[key]), np.median(times_all[key]))