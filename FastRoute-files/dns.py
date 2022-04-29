import os
import sys
import configparser
from flask import Flask, request, jsonify, send_file, send_from_directory
app = Flask(__name__)
last_server_ips = {}
dns_ip = ""

@app.route("/dns/<ip_infor>", methods=['GET'])
def change_DNS(ip_infor):
    id = ip_infor.split('_')[0]
    ip = ip_infor.split('_')[1]
    print(ip_infor.split('_'))

    global last_server_ips
    if str(id) in last_server_ips.keys() and last_server_ips[str(id)] == ip:
        print("no change, still " + ip)
        return "no change, still " + ip
    last_server_ips[str(id)] = ip

    if not os.path.exists("/etc/bind/zones"):
        os.makedirs("/etc/bind/zones")

    template = open('./template_db.example.com').read()
    template += dns_ip
    template += "\n\n"
    for key in last_server_ips.keys():
        template += "server" + str(key) + ".example.com.          IN      A       "
        template += last_server_ips[key]
        template += "\n\n"
        print("server" + key + ".example.com changed to " + last_server_ips[key])

    with open('/etc/bind/zones/db.example.com','w') as f:
        f.write(template)
    os.system("sudo named-checkzone example.com /etc/bind/zones/db.example.com")
    os.system("sudo service bind9 restart")

    return "server.example.com changed"


def default_setting(dns_ip, server_ips, client_ips):
    os.system("sudo cp ./template_named.conf.local /etc/bind/named.conf.local")

    with open("/etc/bind/named.conf.options",'w') as f:
        f.write("acl \"trusted\" {\n")
        f.write("\t" + dns_ip + ";\n")
        for item in client_ips:
            f.write("\t" + item + ";\n")
        f.write("};" + "\n")

        lines = open('./template_named.conf.options').readlines()
        for line in lines:
            if "listen-on {};" in line:
                f.write("\tlisten-on {%s;};\n"%(dns_ip))
                continue
            f.write(line)
    os.system("sudo named-checkconf")

    for i, ip in enumerate(server_ips):
        last_server_ips[str(i + 1)] = ip
    change_DNS("0_" + dns_ip)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('./ip.conf')

    dns_ip = config.get("DNS", "inter")
    server_items = config.items("server")
    server_ips = []
    for item in server_items:
        # if item[0] == 's0' or item[0] == 's3':
        #     print(item[0], item[1])
        # if item[0] in ['s0','s1','s4','s5','s8','s10','s11','s12']:
        server_ips.append(item[1])
    client_ips = config.get("client", "ips").split(',')
    print("DNS server's IP", dns_ip)
    print("Server's IP", server_ips)
    print("Client's IP", client_ips)
    print('\n')

    default_setting(dns_ip=dns_ip, server_ips=server_ips, client_ips=client_ips)

    # app.run(host='0.0.0.0',port=12345)
    app.run(host='0.0.0.0',port=12345)