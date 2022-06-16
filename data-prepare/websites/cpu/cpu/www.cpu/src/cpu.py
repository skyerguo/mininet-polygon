import pymongo
import random
import time

# print("cpu.py")

client = pymongo.MongoClient('198.22.255.15', 27117)
db = client['shuffle_index']
collection = db['shuffle_100000']

def get_ms(ct):
    # ct = time.time()
    local_time = time.localtime(ct)
    data_head = int(time.strftime('%Y%m%d%H%M%S', local_time))
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (str(data_head), data_secs)
    return time_stamp

# n = random.randint(50, 100)
n = 10
# print(n)
# print("start_time: ", get_ms())
st = time.time()

cnt = 0
for i in range(n):
    for item in collection.find({"value": random.randint(0, 100000)}):
        cnt += 1
        # print(str(i + 1) + '/' + str(n))
        # ori_time = get_ms()

# print("done")·

if cnt == n:
    en = time.time()
    print("time_duration: ", en - st)
    # print("end_time: ",get_ms())

# f_out.close()
