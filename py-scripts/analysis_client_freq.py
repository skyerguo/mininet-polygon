import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

root_path = [_ for _ in range(5)]
root_path[0] = "/proj/quic-PG0/data/result-logs/client/2022-07-17_21:28:55/" ## 100
root_path[1] = "/proj/quic-PG0/data/result-logs/client/2022-07-17_20:58:05/" ## 1000
root_path[2] = "/proj/quic-PG0/data/result-logs/client/2022-07-17_21:47:01/" ## 10000
root_path[3] = "/proj/quic-PG0/data/result-logs/client/2022-07-17_22:04:21/" ## 20000
root_path[4] = "/proj/quic-PG0/data/result-logs/client/2022-07-17_22:21:42/" ## 120000


for i in range(5):
    time_point_number = {}

    for client_id in os.listdir(root_path[i]):
        curr_path = root_path[i] + client_id + '/'
        for client_file_name in os.listdir(curr_path):
            if "_2" not in client_file_name:
                continue
            time_stamp = int(int(client_file_name.split("_")[-2]) / 1000) # Transfer to second format.
            if time_stamp not in time_point_number.keys():
                time_point_number[time_stamp] = 1
            else:
                time_point_number[time_stamp] += 1

    # print(time_point_number)
    # temp_data = pd.DataFrame().from_dict(time_point_number)
    temp_data = pd.DataFrame(list(time_point_number.items()), columns=['timestamp', 'number'])
    # print(temp_data)
    # sns.displot(temp_data,  x="timestamp")
    sns.lineplot(data=temp_data, x="timestamp", y="number")
    plt.savefig("../figures/client_freq_%s.png"%(str(i)))