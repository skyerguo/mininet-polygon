import pymongo
import random

client = pymongo.MongoClient('localhost', 27117)
db = client['shuffle_index']
collection = db['shuffle_100000']

obj = {}
a = [x for x in range(100000)]
random.shuffle(a)

for i in range(100000):
    collection.insert_one({'index': i, 'value': a[i]})
# print(obj)