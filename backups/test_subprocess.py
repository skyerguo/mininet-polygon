import subprocess
v = [0, 0, 0]
for i in range(3):
    v[i] = subprocess.run("python3 /data/websites/cpu/cpu/www.cpu/src/cpu.py >> %s.txt"%(i),stderr = subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True,shell=True)
    
print(v[0].stdout)
print(v[1].stdout)
print(v[2].stdout)