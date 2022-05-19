import os
import subprocess
import numpy as np
import sys
import json
import time

data_root_path ="/proj/quic-PG0/data/"

result_root_path = data_root_path + "result-logs/"

server_files = os.listdir(result_root_path + "server")
server_files.sort(reverse=True)


if len(sys.argv) < 2:
    file_order = 0
    print("未输入文件次序，默认选择最新的")
else:
    try:
        file_order = int(sys.argv[1])
        print("选择第%s新的文件"%(str(file_order)))
    except:
        file_order = 0
        print("参数错误，不为int类型，默认选择最新的")

ret = subprocess.Popen("sudo mn -c", shell=True, stdout=subprocess.PIPE)
data=ret.communicate() #如果启用此相会阻塞主程序

ret.wait() #等待子程序运行完毕

start_time = server_files[file_order]
# start_time = "2021-12-02_17:49:32"
print("start_time: ", start_time)

config_file_path = result_root_path + 'config/' + str(start_time) + '/topo.json'
config_file = json.load(open(config_file_path, 'r'))

plt_total = {"latency": [], "throughput": [], "cpu": [], "mongo": []}
req_total_number = {"latency": 0, "throughput": 0, "cpu": 0}
bind_dispatcher_success_number = {"latency": 0, "throughput": 0, "cpu": 0}
success_rate_per_client = [[] for _ in range(config_file['client_number'])]

saved_results_root_path = data_root_path + "saved_results/" + str(start_time) + "/"
os.system("sudo rm -rf %s" %(saved_results_root_path))
# print(os.listdir(saved_logs))

# server_number = 0
# server_id = {}
# for server_file in os.listdir(result_root_path + "server/" + start_time):
#     if server_file.split("_")[0] not in server_id:
#         server_id[server_file.split("_")[0]] = 1
#         server_number += 1


print("client_number: ", config_file['client_number'])
print("client_thread: ", config_file['client_thread'])
print("server_number: ", config_file['server_number'])
print("dispatcher_number: ", config_file['dispatcher_number'])
if 'mode' in config_file:
    print("mode: ", config_file['mode'])

cnt_process_limit = 0

## client data
earliest_request_time = 100000000000000
latest_request_time = 0

client_port_hashtable = {}

plt_throughput_per_zone = [[] for _ in range(config_file['dispatcher_number'])]

server_cpu_per_second = [{} for _ in range(config_file['server_number'])]

for client_id in range(config_file['client_number']):
    client_result_path = result_root_path + "client/" + str(start_time) + "/" + str(client_id) + "/"
    client_files = os.listdir(client_result_path)
    # print(len(client_files))
    client_files.sort()

    for client_file in client_files:
        if "_1.txt" in client_file:
            plt = 0
            sensitive_type = ""
            current_time = 0
            mode = "Polygon"
            cpu_duration = 0
            min_st = -1
            max_en = 0
            plt_times = 0
            cnt_mongo = 0
            bind_dispatcher_success_flag = 0
            success_rate_per_client[client_id].append(0)
            remote_server_id = -1
            continue
        
        if "_2.txt" in client_file:
            earliest_request_time = min(earliest_request_time, int(client_file.split('_')[-2]))
            latest_request_time = max(latest_request_time, int(client_file.split('_')[-2]))
            with open(client_result_path + client_file, "r") as f:
                for line in f:
                    if "Resource temporarily unavailable" in line:
                        cnt_process_limit += 1
                    if "PLT:" in line:
                        plt = int(line.split(" ")[1].strip())
                        plt_times += 1
                    if "bind fd_" in line:
                        remote_server_id = int(line.split(".")[2].strip())
                    if "bind fd2_" in line:
                        remote_server_id = int(line.split(".")[2].strip())
                        bind_dispatcher_success_flag = 1
        
        if "_3.txt" in client_file:
            with open(client_result_path + client_file, "r") as f:
                for line in f:
                    # if "st:" in line:
                    #     curr_st = float(line.split(" ")[-1].strip())

                    # if "en:" in line:
                    #     cnt_mongo += 1
                    #     curr_en = float(line.split(" ")[-1].strip())
                    #     cpu_duration += int((curr_en - curr_st) * 1000000)
                    if "st:" in line:
                        curr_st = float(line.split(" ")[-1].strip())
                        if min_st == -1:
                            min_st = curr_st
                        else:
                            min_st = min(min_st, curr_st)
                    if "en:" in line:
                        cnt_mongo += 1
                        curr_en = float(line.split(" ")[-1].strip())
                        max_en = max(max_en, curr_en)
                    
                        for time_stamp in range(int(curr_st), int(curr_en) + 1):
                            if time_stamp in  server_cpu_per_second[remote_server_id].keys():
                                server_cpu_per_second[remote_server_id][time_stamp] += 1
                            else:
                                server_cpu_per_second[remote_server_id][time_stamp] = 1

                        if cnt_mongo == 100:
                            cpu_duration = int((max_en - min_st) * 1000000)
                    

        if "_tmp.txt" in client_file:
            client_ip = "10.0.%s.1" % (client_file.split("_")[0])
            client_port = client_file.split("_")[1]
            
            # hash_key = client_file.split("_")[0] + client_port
            # if hash_key not in client_port_hashtable: ## 去掉每个client+port的第一个请求，考虑热启动，提高成功率
            #     client_port_hashtable[hash_key] = 1
            #     continue
            # elif client_port_hashtable[hash_key] == 1: ## 去掉每个client+port的第二个请求，考虑热启动，提高成功率
            #     client_port_hashtable[hash_key] = 2
            #     continue

            with open(client_result_path + client_file, "r") as f:
                for line in f:
                    if "data_type" in line:
                        if "normal_1" in line:
                            sensitive_type = "latency"
                        elif "cpu" in line:
                            sensitive_type = "cpu"
                        elif "video" in line:
                            sensitive_type = "throughput"
                        else:
                            sensitive_type = "error"
                    if ("current_time") in line:
                        current_time = line.split(" ")[-1].strip()
                    if ("mode") in line:
                        mode = line.split(" ")[-1].strip()

            os.system("mkdir -p %s" %(saved_results_root_path + mode + "/" + str(client_ip) + "_jct/"))

            req_total_number[sensitive_type] += 1
            bind_dispatcher_success_number[sensitive_type] += bind_dispatcher_success_flag

            if plt == 0: # 应该有plt，但是没有查到
                continue
            # print(plt, plt_times)
            # if sensitive_type == "cpu":
            #     print(plt, plt_times, cpu_duration)
            #     print(client_file)
            # if plt_times != 2 and sensitive_type != "cpu": # throughput和latency应该都是两个plt
            #     continue
            if plt_times != 2: # 所有应该都是两个plt
                continue
            if sensitive_type == "cpu" and cnt_mongo != 100:
                print("未完成的cpu请求完成度", cnt_mongo, "/100")
            if sensitive_type == "cpu" and (cpu_duration == 0 or cnt_mongo != 100): # 应该是cpu，但是没查到cpu，或者查询次数不对（这里数字要和dispathcer.cc中的对应）
                continue
            # if cpu_duration > 100 * 1000000:
            #     print("zone: ", config_file['client_zone'][client_id], "cpu_duration: ", cpu_duration / 1000000)

            plt = plt + cpu_duration

            success_rate_per_client[client_id][-1] = 1
            
            plt_total[sensitive_type].append(float(plt))
            if sensitive_type == "cpu":
                plt_total["mongo"].append(float(cpu_duration))

            if sensitive_type == "throughput":
                plt_throughput_per_zone[config_file['client_zone'][client_id]].append(float(plt))

            print(str(current_time) + " " + sensitive_type + " " + str(plt), file=open(saved_results_root_path + mode + "/" + str(client_ip) + "_jct/" + str(client_ip) + "_" + str(client_port) + ".txt", "a"))
    
    # print("plt_latency_avg: ", np.mean(plt_total["latency"]) / 1000000, "\t数量: ", len(plt_total["latency"]), "\t成功率: ", str(len(plt_total["latency"]) / req_total_number["latency"] * 100) + "%")
    # print("plt_throughput_avg: ", np.mean(plt_total["throughput"]) / 1000000, "\t数量: ", len(plt_total["throughput"]), "\t成功率: ", str(len(plt_total["throughput"]) / req_total_number["throughput"] * 100) + "%")
    # print("plt_cpu_avg: ", np.mean(plt_total["cpu"]) / 1000000, "\t数量: ", len(plt_total["cpu"]), "\t成功率: ", str(len(plt_total["cpu"]) / req_total_number["cpu"] * 100) + "%")



if config_file['mode'] == "Polygon":
    ## 计算每种sensitive的cross region比例
    cross_region = {"cpu": 0, "latency": 0, "throughput": 0}
    local_region = {"cpu": 0, "latency": 0, "throughput": 0}
    throughput_cross_to = [0 for _ in range(config_file['dispatcher_number'])]

    for dispatcher_id in range(config_file['dispatcher_number']):
        dispatcher_result_path = result_root_path + "dispatcher/" + str(start_time) + "/" + str(dispatcher_id) + "/"
        dispatcher_files = os.listdir(dispatcher_result_path)

        for dispatcher_file in dispatcher_files: # 因为一个文件里面会有多个转发记录，判断完整转发才记录
            if ("_2.txt") in dispatcher_file:
                dispatcher_ip = "10.0.%s.5" % (dispatcher_file.split("_")[0])

                forward_region = 0 # 0表示local, 1表示cross
                sensitive_type = ""
                with open(dispatcher_result_path + dispatcher_file, "r") as f:
                    for line in f:
                        if "local_best_value" in line:
                            local_best_value = float(line.split(":")[1].strip())
                        if "sensitive_type" in line:
                            sensitive_type = line.split(":")[1].strip()
                        if "!Forwarded to" in line:
                            if "remote" in line:
                                forward_region = 1
                                forward_best_value = float(line.split(" ")[-1].strip())
                                # if sensitive_type == "throughput":
                                    # print(sensitive_type, local_best_value, forward_best_value)
                            else:
                                forward_region = 0
                                # if sensitive_type == "cpu":
                                #     print(sensitive_type, local_best_value)
                            # print(dispatcher_file, forward_region)
                            # print(sensitive_type)
                            cross_region[sensitive_type] += forward_region
                            local_region[sensitive_type] += 1-forward_region
                            if sensitive_type == 'throughput':
                                throughput_cross_to[int(dispatcher_file.split("_")[0])] += forward_region
                            
   


# ## dispatcher data
# dispatcher_result_path = result_root_path + "dispatcher/" + str(start_time) + "/"
# dispatcher_files = os.listdir(dispatcher_result_path)
# dispatcher_files.sort()

# for dispatcher_file in dispatcher_files: # 因为一个文件里面会有多个转发记录，判断完整转发才记录
#     if ("_1.txt") in dispatcher_file:
#         current_time = 0
#         client_ip = ""
#         sensitive_type = ""
#         foward_to = ""
#         forward_dc = ""
#         server_ip = ""
#         continue

#     if ("_2.txt") in dispatcher_file:
#         dispatcher_ip = "10.0.%s.5" % (dispatcher_file.split("_")[0])
#         with open(dispatcher_result_path + dispatcher_file, "r") as f:
#             for line in f:
#                 if ("client_ip") in line:
#                     client_ip = line.split(" ")[-1].strip()
#                 if ("current_time") in line:
#                     current_time = line.split(" ")[-1].strip()
#                 if ("sensitive_type") in line:
#                     if "latency" in line:
#                         sensitive_type = "latency"
#                     elif "cpu" in line:
#                         sensitive_type = "cpu"
#                     elif "throughput" in line:
#                         sensitive_type = "throughput"
#                     else:
#                         sensitive_type = "error"
#                     # sensitive_type = line.split(" ")[-1].strip()
#                 if ("!Forwarded") in line:
#                     forward_server_id = line.split(" ")[-2].strip()
#                     server_ip = "10.0.%s.3" % (str(forward_server_id))
#                     if ("local") in line:
#                         forward_to = "local"
#                     elif ("remote") in line:
#                         forward_to = "remote"

#                     os.system("mkdir -p %s" %(saved_results_root_path + mode + "/" + dispatcher_ip + "_routing/"))

#                     if (client_ip == ""):
#                         continue
                    
#                     print(str(current_time) + " " + client_ip + " " + sensitive_type + " " + forward_to + " " + server_ip, file=open(saved_results_root_path + mode + "/" + dispatcher_ip + "_routing/" + "routing.txt", "a"))

#                     current_time = 0
#                     client_ip = ""
#                     sensitive_type = ""
#                     foward_to = ""
#                     forward_dc = ""
#                     server_ip = ""

#     if ("_tmp.txt") in dispatcher_file:
#         continue

# ## measurement data
# measurement_result_path = data_root_path + "measurement_log/" + str(start_time) + "/record/"
# measurement_files = os.listdir(measurement_result_path)
# measurement_files.sort()

# server_number = 0
# server_id = {}
# for server_file in os.listdir(result_root_path + "server/" + start_time):
#     if server_file.split("_")[0] not in server_id:
#         server_id[server_file.split("_")[0]] = 1
#         server_number += 1

# config_file_path = result_root_path + 'config/' + str(start_time) + '/topo.json'
# config_file = json.load(open(config_file_path, 'r'))
# print("client_number: ", config_file['client_number'])
# print("server_number: ", server_number)
# print("dispatcher_number: ", config_file['dispatcher_number'])

# for measurement_file in measurement_files:
#     dispatcher_ip = "10.0.%s.5"%(measurement_file.split('.')[0])
#     throughput = [-1 for _ in range(server_number)]
#     cpu = [-1 for _ in range(server_number)]
#     with open(measurement_result_path + measurement_file, "r") as f:
#         for line in f:
#             if not "current_time" in line:
#                 # dispatcher_ip = "10.0.%s.5"%(line.split("+")[0].strip())
#                 server_id = int(line.split("+")[0].strip())
#                 temp_throughput = line.split('+')[1].strip()
#                 temp_cpu = line.split('+')[2].strip()
#                 if not temp_throughput:
#                     temp_throughput = -1
#                 if not temp_cpu:
#                     temp_cpu = -1
#                 throughput[server_id] = temp_throughput
#                 cpu[server_id] = temp_cpu
#             else:
#                 os.system("mkdir -p " + saved_results_root_path + mode + "/" + dispatcher_ip + "_throughput/")
#                 with open(saved_results_root_path + mode + "/" + dispatcher_ip + "_throughput/throughput.txt", "a") as f_out:
#                     print(current_time,end=" ", file=f_out)
#                     for i in range(server_number):
#                         print(throughput[i], end=" ", file=f_out)
#                     print(" ", file=f_out)
#                 os.system("mkdir -p " + saved_results_root_path + mode + "/" + dispatcher_ip + "_cpu/")
#                 with open(saved_results_root_path + mode + "/" + dispatcher_ip + "_cpu/cpu.txt", "a") as f_out:
#                     print(current_time,end=" ", file=f_out)
#                     for i in range(server_number):
#                         print(cpu[i], end=" ", file=f_out)
#                     print(" ", file=f_out)

#                 current_time = line.split(' ')[-1].strip()


# print(latest_request_time, earliest_request_time)
timeArray = time.strptime(start_time, "%Y-%m-%d_%H:%M:%S")
# print(earliest_request_time)
# print(start_time)
# print(time.mktime(timeArray))
print("实验初始化时长:\t", earliest_request_time / 1000 - time.mktime(timeArray), "秒")
print("实际请求总时长:\t", (latest_request_time - earliest_request_time) / 1000, "秒")

print(" === plt analysis result === ")
print("plt_latency_avg: ", np.mean(plt_total["latency"]) / 1000000, "\t成功数量: ", len(plt_total["latency"]), "\t成功率: ", str(round(len(plt_total["latency"]) / req_total_number["latency"] * 100, 1)) + "%")
print("plt_throughput_avg: ", np.mean(plt_total["throughput"]) / 1000000, "\t成功数量: ", len(plt_total["throughput"]), "\t成功率: ", str(round(len(plt_total["throughput"]) / req_total_number["throughput"] * 100, 1)) + "%")
print("plt_cpu_avg: ", np.mean(plt_total["cpu"]) / 1000000, "\t成功数量: ", len(plt_total["cpu"]), "\t成功率: ", str(round(len(plt_total["cpu"]) / req_total_number["cpu"] * 100, 1)) + "%")
print("mongo_duration: ", "平均值: ", np.mean(plt_total["mongo"]) / 1000000, "\t中位数: ", np.median(plt_total["mongo"]) / 1000000)

if (config_file['mode'] == 'Polygon'):
    print(" === Polygon === ")
    for sensitive_type in ["latency", "throughput", "cpu"]:
        print(sensitive_type, "\t跨地区数量: ", cross_region[sensitive_type], "\t跨地区成功率: ", cross_region[sensitive_type] / (cross_region[sensitive_type] + local_region[sensitive_type]))
        # print(sensitive_type, "\t绑定dispatcher成功率" + str(round(bind_dispatcher_success_number[sensitive_type] / req_total_number[sensitive_type] * 100, 1)) + "%")
    for dispatcher_id in range(config_file['dispatcher_number']):
        print('第', str(dispatcher_id), '个zone的请求转发个数: \t', throughput_cross_to[dispatcher_id])

for dispatcher_id in range(config_file['dispatcher_number']):
    print('第', str(dispatcher_id), '个zone的throughput请求plt: \t', np.mean(plt_throughput_per_zone[dispatcher_id]) / 1000000, "\t成功数量: ", len(plt_throughput_per_zone[dispatcher_id]))

# print("Resource temporarily unavailable number: ", cnt_process_limit)
# print(" === success_rate_per_client === ")
# for client_id in range(config_file['client_number']):
#     print(client_id, str(round(np.sum(success_rate_per_client[client_id]) / len(success_rate_per_client[client_id]) * 100, 1)) + "%")

print(" === 每个server的CPU请求数量 === ")
for server_id in range(config_file['server_number']):
    request_count = []
    for time_stamp in server_cpu_per_second[server_id]:
        request_count.append(server_cpu_per_second[server_id][time_stamp])
    print("server: ", server_id, "avg_cpu_request_per_second: ", np.mean(request_count))
    # print(server_cpu_per_second[server_id])