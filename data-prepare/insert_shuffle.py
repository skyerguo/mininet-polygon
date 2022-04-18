import pymongo
import random

client = pymongo.MongoClient('localhost', 27117)
db = client['shuffle_index']
collection = db['shuffle_1000000']

obj = {}
a = [x for x in range(1000000)]
random.shuffle(a)

for i in range(1000000):
    collection.insert_one({'index': i, 'value': a[i]})
# print(obj)