import pymongo
import random
import time

# print("cpu.py")

client = pymongo.MongoClient('198.22.255.12', 27117)
db = client['shuffle_index']
db_size = 100000
collection = db['shuffle_%s'%(db_size)]

def get_ms(ct):
    # ct = time.time()
    local_time = time.localtime(ct)
    data_head = int(time.strftime('%Y%m%d%H%M%S', local_time))
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (str(data_head), data_secs)
    return time_stamp

n = 10
st = time.time()

cnt = 0
for i in range(n):
    collection.find_one({"value": random.randint(0, db_size)}, {"status":0,"_id":0})
    cnt += 1

if cnt == n:
    en = time.time()
    print("time_duration: ", en - st)