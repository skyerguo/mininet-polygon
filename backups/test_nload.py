import re

data_path = "/data/measurement_log/2022-02-28_11:03:00/nload/nload_log_3_3_4.txt"
f = open(data_path, "r")
cnt = 0

# # ret1 = "\x1b[10d\x1b[H\x1b[2JDevice c3-eth4 (1/1):\n"
# ret1 = "\x1b[2d=\x1b[78b=\x1b[3;1HIncoming:\x1b[3;41HOutgoing:\n"
# ret = re.sub("\x1b\[[0-9]*\;[0-9]*[bdHJ]", "", ret1, 0)
# ret = re.sub("\x1b\[[0-9]*[bdHJ]", "", ret, 0)
# print(ret)

for line in f:
    cnt += 1
    # print(cnt)
    ret = re.sub("\x1b\[[?]*[0-9]*[a-zA-Z]", "", line, 0)
    ret = re.sub("\x1b\[[?]*[0-9]*\;[0-9]*[a-zA-Z=]", "\t", ret, 0)
    ret = re.sub("\x1b\[[?]*[0-9]*\;[0-9]*\;[0-9]*[a-zA-Z=]", "", ret, 0)
    ret = re.sub("\x1b\([a-zA-Z]", "", ret, 0)
    ret = re.sub("\x1b=", "", ret, 0)
    if "\x1b" in ret:
        print(ret.split(" "))
    print(line.split(" "))
    break
    # print(line.split(" "))

# sed -r "s/\x1b\[[?]*[0-9]*[a-zA-Z]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b\\([a-zA-Z]//g; s/\x1b=//g" nload_log_3_3_4.txt

data_path = "/home/mininet/nload.txt"
f = open(data_path, "r")
for line in f:
    print(line.split(" "))
    break