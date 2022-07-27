import subprocess
import os
import ipaddress
import time
from time import sleep
from threading import Thread
from unicodedata import name
import os 

from datetime import datetime
import json

# first we get the current timestamp
T_NOW = time.time()
print("Timestamp: ", T_NOW)

FILE_NAME = "ping_output.json"

# Dest IP
IP_H3 = "10.0.0.3"

# 15000 - 28 byte for header
SIZE = "14972" 

# 1 packet / 1 sec = 1.5 KB / 1 sec
RATE = "1" 

# ping -c 1 -s 14972 10.0.0.3 
# ping -c 20 -s 14972 -i 1 10.0.0.3 

RESULT = {}

def ping_host(i):
    output = subprocess.run(["ping", "-c", "1", "-s", SIZE, IP_H3], stdout=subprocess.PIPE, encoding="utf-8")
    print(output.stdout)
    sttime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    RESULT[i] = {"Timestamp":sttime, "Output":output.stdout}

if __name__ == "__main__":
    threads = []       
    for i in range(1,51):
        thread = Thread(target=ping_host, args=(i,))
        threads.append(thread)
        thread.start()

        # Increase Rate
        sleep(1)
    
    for t in threads:
        t.join()
    
    with open(FILE_NAME, "w") as file:
        json.dump(RESULT, file)