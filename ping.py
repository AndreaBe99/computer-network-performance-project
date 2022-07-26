import subprocess
import os
import ipaddress
import time
from time import sleep
from threading import Thread
from unicodedata import name
import os 

from datetime import datetime
import time
import json
import re

LAST_PING = "last_ping.json"
PING_LIST = "ping_list.json"

## PLOT 1
MAX_NUM_PACKET = 70

# Dest IP
IP_H3 = "10.0.0.3"

# 15000 - 28 byte for header
SIZE = "14972" 
# 10000 - 28 byte for header
#SIZE = "9972" 

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
    # 100% packet loss
    else:
        rtt_dict["min"] = -1
        rtt_dict["avg"] = -1
        rtt_dict["max"] = -1
        rtt_dict["mdev"] = -1

    sttime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    RESULT[sttime] = {"Timestamp":sttime, "Rtt": rtt_dict}

    with open(LAST_PING, "w") as file:
        json.dump(RESULT[sttime], file)


if __name__ == "__main__":
    workers = []       
    """
    ########## For Plot 1 ##########
    for i in range(1, MAX_NUM_PACKET, 2):
        end = time.time() + 1  # 10 sec * 10 iteration = 100 sec 
        while time.time() < end:
            worker = Thread(target=ping_host, args=(i,))
            workers.append(worker)
            worker.setDaemon(True)
            worker.start()
            sleep(1/i)
        for w in workers:
            w.join()
    ################################
    """
    ########### For plot 2-3-4 ##########
    # The DoS Attack have to start after 10 minute so we want to perfrom a 15 minute test
    # One thread at sec for 15 minute == 1200 threads
    end = time.time() + 60 * 15  # 15 minutes 
    i = 0
    while time.time() < end:
    # for i in range(1, MAX_NUM_PACKET+1):
        worker = Thread(target=ping_host, args=(i,))
        workers.append(worker)
        worker.setDaemon(True)
        worker.start()
        sleep(1)
        i += 1
        
    for w in workers:
        w.join()
    #####################################
    
    with open(PING_LIST, "w") as file:
        json.dump(RESULT, file)


