import os

client_data_root_path = '/data/result-logs/client/'
client_data_path_list = sorted(os.listdir(client_data_root_path), reverse=True)
# print(client_data_path_list)
client_data_path = os.path.join(client_data_root_path, client_data_path_list[0])

total_num = 0
success_num = 0
err_tls_num = 0
err_conn_num = 0
for file_name in os.listdir(client_data_path):
    if not file_name.endswith("_2.txt"):
        continue
    total_num += 1
    
    with open(os.path.join(client_data_path, file_name)) as f:
        for line in f:
            if line.startswith("last_plt_cost:"):
                success_num += 1
                break
            if "ERR_TLS_DECRYPT" in line:
                err_tls_num += 1
                break
            if "ERR_INVALID_STATE" in line:
                err_conn_num += 1
                break

print("success/total: ", success_num, total_num)
print("error_tls/total: ", err_tls_num, total_num)
print("error_connection/total: ", err_conn_num, total_num)
print("success ratio: ", success_num / total_num)