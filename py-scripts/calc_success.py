import os

client_data_root_path = '/data/result-logs/client/'
client_data_path_list = sorted(os.listdir(client_data_root_path), reverse=True)
# print(client_data_path_list)
client_data_path = os.path.join(client_data_root_path, client_data_path_list[0])

total_num = 0
success_num = 0
for file_name in os.listdir(client_data_path):
    if not file_name.endswith("_2.txt"):
        continue
    total_num += 1
    
    with open(os.path.join(client_data_path, file_name)) as f:
        for line in f:
            if line.startswith("last_plt_cost:"):
                success_num += 1
                break

print("success/total: ", success_num, total_num)
print("success ratio: ", success_num / total_num)