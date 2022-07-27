import subprocess
import os
import ipaddress
import time
from time import sleep
from threading import Thread
from unicodedata import name
import os 

from datetime import datetime

# first we get the current timestamp
T_NOW = time.time()
print("Timestamp: ", T_NOW)

FILE_NAME = "ping_output.txt"

# Dest IP
IP_H3 = "10.0.0.3"

# 15000 - 28 byte for header
SIZE = "14972" 

# 1 packet / 1 sec = 1.5 KB / 1 sec
RATE = "1" 

# ping -c 1 -s 14972 10.0.0.3 
# ping -c 20 -s 14972 -i 1 10.0.0.3 

def ping_host(i):
    output = subprocess.run(["ping", "-c", "1", "-s", SIZE, IP_H3], stdout=subprocess.PIPE, encoding="utf-8")
    #output = subprocess.run(["ping", "-c", "20", "-i", RATE, "-s", SIZE, IP_H3], stdout=subprocess.PIPE, encoding="utf-8")
    print(output.stdout)
    with open(FILE_NAME, "a+") as file:
        sttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write("Timestamp: " + sttime + "\n")
        file.write(output.stdout)
        file.write("\n")


if __name__ == "__main__":
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
        with open(FILE_NAME, 'w') as f:
            pass

    threads = []       
    for i in range(1,10,2):
        thread = Thread(target=ping_host, args=(i,))
        threads.append(thread)
        thread.start()

        # Increase Rate
        sleep(1/i)
    
    for t in threads:
        t.join()