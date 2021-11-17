import os
import subprocess

data_root_path = "/data/"

result_root_path = data_root_path + "result-logs/"

server_files = os.listdir(result_root_path + "server")
server_files.sort(reverse=True)

start_time = server_files[0]

saved_results_root_path = data_root_path + "saved_results/" + str(start_time) + "/"
# print(os.listdir(saved_logs))

client_result_path = result_root_path + "client/" + str(start_time) + "/"
client_files = os.listdir(client_result_path)
client_files.sort()

for client_file in client_files:
    if "_1" in client_file:
        plt = 0
        sensitive_type = ""
        current_time = 0
        mode = "Polygon"
        continue
    
    if "_2" in client_file:
        ret = subprocess.Popen("tac %s | grep -a 'PLT' |head -n 1| awk '{print $2}'"%(client_result_path + client_file), shell=True,stdout=subprocess.PIPE)
        plt = ret.stdout.read().decode("utf-8").strip('\n')
        ret.stdout.close()
    
    if "_tmp" in client_file:
        client_ip = "10.0.%s.1" % (client_file.split("_")[0])
        client_port = client_file.split("_")[1]

        with open(client_result_path + client_file, "r") as f:
            for line in f:
                if "data_type" in line:
                    if "normal_1" in line:
                        sensitive_type = "delay"
                    if "cpu" in line:
                        sensitive_type = "cpu"
                    if "video" in line:
                        sensitive_type = "bw"
                if ("--time_stamp") in line:
                    current_time = line.split(" ")[-1].strip()
                if ("mode") in line:
                    mode = line.split(" ")[-1].strip()

        os.system("mkdir -p %s" %(saved_results_root_path + mode))
        
        print(current_time + " " + sensitive_type + " " + str(plt), file=open(saved_results_root_path + mode + "/" + client_ip + "_jct/" + client_ip + "_" + client_port + ".txt", "a"))

dispatcher_result_path = result_root_path + "dispatcher/" + str(start_time) + "/"
dispatcher_files = os.listdir(dispatcher_result_path)
dispatcher_files.sort()

for dispatcher_file in dispatcher_files: # 因为一个文件里面会有多个转发记录，判断完整转发才记录
    if ("_1") in dispatcher_file:
        current_time = 0
        client_ip = ""
        sensitive_type = ""
        foward_to = ""
        forward_dc = ""
        server_ip = ""
        continue

    if ("_2") in dispatcher_file:
        dispatcher_ip = "10.0.%s.3" % (dispatcher_file.split("_")[0])

        with open(dispatcher_result_path + dispatcher_file, "r") as f:
            if ("client_ip") in line:
                client_ip = line.split(" ")[-1].strip()
            if ("current_time") in line:
                current_time = line.split(" ")[-1].strip()
            if ("sensitive_type") in line:
                sensitive_type = line.split(" ")[-1].strip()
            if ("!Forwarded") in line:
                forward_dc = line.split(" ")[5].strip()
                server_ip = "10.0.%s.5" % (str(forward_dc))
                if ("server") in line:
                    forward_to = "local"
                elif ("dispatcher") in line:
                    forward_to = "forward"
                
                print(current_time + " " + client_ip + " " + sensitive_type + " " + forward_to + " " + server_ip, file=open(saved_results_root_path + mode + "/" + dispatcher_ip + "_routing/" + "routing.txt", "a"))

                current_time = 0
                client_ip = ""
                sensitive_type = ""
                foward_to = ""
                forward_dc = ""
                server_ip = ""

    if ("_tmp") in dispatcher_file:
        continue
            