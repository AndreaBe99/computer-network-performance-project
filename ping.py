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
import re

# first we get the current timestamp
T_NOW = time.time()
print("Timestamp: ", T_NOW)

LAST_PING = "last_ping.json"
PING_LIST = "ping_list.json"

# Dest IP
IP_H3 = "10.0.0.3"

# 15000 - 28 byte for header
SIZE = "14972" 
# 20000 - 28 = 9972

# 1 packet / 1 sec = 1.5 KB / 1 sec
RATE = "1" 

# ping -c 1 -s 14972 10.0.0.3 
# ping -c 20 -s 14972 -i 1 10.0.0.3 

RESULT = {}

def ping_host(i):
    output = subprocess.run(["ping", "-c", "1", "-s", SIZE, IP_H3], stdout=subprocess.PIPE, encoding="utf-8")
    print(output.stdout)
    rtt = re.findall("min/avg/max/mdev = (.*)ms\n", output.stdout)
    rtt_dict = {}
    if len(rtt) > 0:
        rtt_split = rtt[0].split("/")
        rtt_dict["min"] = rtt_split[0]
        rtt_dict["avg"] = rtt_split[1]
        rtt_dict["max"] = rtt_split[2]
        rtt_dict["mdev"] = rtt_split[3]

        sttime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        RESULT[i] = {"Timestamp":sttime, "Rtt": rtt_dict, "Output":output.stdout}

        with open(LAST_PING, "w") as file:
            json.dump(RESULT[i], file)


def plot_1(threads):
    for i in range(1,31):
        thread = Thread(target=ping_host, args=(i,))
        threads.append(thread)
        thread.start()
        # Increase Rate
        sleep(1/i)

    return threads

def plot_2(threads):
    for i in range(1,101):
        thread = Thread(target=ping_host, args=(i,))
        threads.append(thread)
        thread.start()
        # Increase Rate
        sleep(1)

    return threads

if __name__ == "__main__":
    threads = []       
    # threads = plot_1(threads) 
    threads = plot_2(threads) 

    for t in threads:
        t.join()
    
    with open(PING_LIST, "w") as file:
        json.dump(RESULT, file)

