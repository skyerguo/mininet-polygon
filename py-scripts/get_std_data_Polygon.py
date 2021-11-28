import os
import subprocess

data_root_path = "/data/"

result_root_path = data_root_path + "result-logs/"

server_files = os.listdir(result_root_path + "server")
server_files.sort(reverse=True)

start_time = server_files[0]
# start_time = "2021-11-28_00:52:53"

saved_results_root_path = data_root_path + "saved_results/" + str(start_time) + "/"
os.system("sudo rm -rf %s" %(saved_results_root_path))
# print(os.listdir(saved_logs))

## client data
client_result_path = result_root_path + "client/" + str(start_time) + "/"
client_files = os.listdir(client_result_path)
client_files.sort()

for client_file in client_files:
    if "_1.txt" in client_file:
        plt = 0
        sensitive_type = ""
        current_time = 0
        mode = "Polygon"
        cpu_duration = 0
        continue
    
    if "_2.txt" in client_file:
        with open(client_result_path + client_file, "r") as f:
            for line in f:
                if "PLT:" in line:
                    plt = int(line.split(" ")[1].strip())
                if "start_time:" in line:
                    cpu_start_time = float(line.split(" ")[-1].strip())
                if "end_time:" in line:
                    cpu_end_time = float(line.split(" ")[-1].strip())
                    cpu_duration = int((cpu_end_time - cpu_start_time) * 1000000)

    if "_tmp.txt" in client_file:
        client_ip = "10.0.%s.1" % (client_file.split("_")[0])
        client_port = client_file.split("_")[1]

        with open(client_result_path + client_file, "r") as f:
            for line in f:
                if "data_type" in line:
                    if "normal_1" in line:
                        sensitive_type = "delay"
                    elif "cpu" in line:
                        sensitive_type = "cpu"
                    elif "video" in line:
                        sensitive_type = "bw"
                    else:
                        sensitive_type = "error"
                if ("current_time") in line:
                    current_time = line.split(" ")[-1].strip()
                if ("mode") in line:
                    mode = line.split(" ")[-1].strip()

        os.system("mkdir -p %s" %(saved_results_root_path + mode + "/" + str(client_ip) + "_jct/"))

        if sensitive_type == "cpu" and cpu_duration == 0: # 应该是cpu，但是没查到cpu
            continue
        if plt == 0: # 应该有plt，但是没有查到
            continue
        
        print(str(current_time) + " " + sensitive_type + " " + str(plt), file=open(saved_results_root_path + mode + "/" + str(client_ip) + "_jct/" + str(client_ip) + "_" + str(client_port) + ".txt", "a"))

## dispatcher data
dispatcher_result_path = result_root_path + "dispatcher/" + str(start_time) + "/"
dispatcher_files = os.listdir(dispatcher_result_path)
dispatcher_files.sort()

for dispatcher_file in dispatcher_files: # 因为一个文件里面会有多个转发记录，判断完整转发才记录
    if ("_1.txt") in dispatcher_file:
        current_time = 0
        client_ip = ""
        sensitive_type = ""
        foward_to = ""
        forward_dc = ""
        server_ip = ""
        continue

    if ("_2.txt") in dispatcher_file:
        dispatcher_ip = "10.0.%s.5" % (dispatcher_file.split("_")[0])
        with open(dispatcher_result_path + dispatcher_file, "r") as f:
            for line in f:
                if ("client_ip") in line:
                    client_ip = line.split(" ")[-1].strip()
                if ("current_time") in line:
                    current_time = line.split(" ")[-1].strip()
                if ("sensitive_type") in line:
                    if "latency" in line:
                        sensitive_type = "delay"
                    elif "cpu" in line:
                        sensitive_type = "cpu"
                    elif "throughput" in line:
                        sensitive_type = "bw"
                    else:
                        sensitive_type = "error"
                    # sensitive_type = line.split(" ")[-1].strip()
                if ("!Forwarded") in line:
                    forward_dc = line.split(" ")[5].strip()
                    server_ip = "10.0.%s.3" % (str(forward_dc))
                    if ("server") in line:
                        forward_to = "local"
                    elif ("dispatcher") in line:
                        forward_to = "forward"

                    # print(3333)

                    os.system("mkdir -p %s" %(saved_results_root_path + mode + "/" + dispatcher_ip + "_routing/"))
                    
                    print(str(current_time) + " " + client_ip + " " + sensitive_type + " " + forward_to + " " + server_ip, file=open(saved_results_root_path + mode + "/" + dispatcher_ip + "_routing/" + "routing.txt", "a"))

                    current_time = 0
                    client_ip = ""
                    sensitive_type = ""
                    foward_to = ""
                    forward_dc = ""
                    server_ip = ""

    if ("_tmp.txt") in dispatcher_file:
        continue
                    
## measurement data
measurement_result_path = data_root_path + "measurement_log/" + str(start_time) + "/record/"
measurement_files = os.listdir(measurement_result_path)
measurement_files.sort()

server_number = 0
server_id = {}
for server_file in os.listdir(result_root_path + "server/" + start_time):
    if server_file.split("_")[0] not in server_id:
        server_id[server_file.split("_")[0]] = 1
        server_number += 1
print("server_number: ", server_number)

for measurement_file in measurement_files:
    dispatcher_ip = "10.0.%s.5"%(measurement_file.split('.')[0])
    bw = [-1 for _ in range(server_number)]
    cpu = [-1 for _ in range(server_number)]
    with open(measurement_result_path + measurement_file, "r") as f:
        for line in f:
            if not "current_time" in line:
                # dispatcher_ip = "10.0.%s.5"%(line.split("+")[0].strip())
                server_id = int(line.split("+")[0].strip())
                temp_bw = line.split('+')[1].strip()
                temp_cpu = line.split('+')[2].strip()
                if not temp_bw:
                    temp_bw = -1
                if not temp_cpu:
                    temp_cpu = -1
                bw[server_id] = temp_bw
                cpu[server_id] = temp_cpu
            else:
                os.system("mkdir -p " + saved_results_root_path + mode + "/" + dispatcher_ip + "_bw/")
                with open(saved_results_root_path + mode + "/" + dispatcher_ip + "_bw/bw.txt", "a") as f_out:
                    print(current_time,end=" ", file=f_out)
                    for i in range(server_number):
                        print(bw[i], end=" ", file=f_out)
                    print(" ", file=f_out)
                os.system("mkdir -p " + saved_results_root_path + mode + "/" + dispatcher_ip + "_cpu/")
                with open(saved_results_root_path + mode + "/" + dispatcher_ip + "_cpu/cpu.txt", "a") as f_out:
                    print(current_time,end=" ", file=f_out)
                    for i in range(server_number):
                        print(cpu[i], end=" ", file=f_out)
                    print(" ", file=f_out)

                current_time = line.split(' ')[-1].strip()