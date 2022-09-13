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
# NUM_THREAD = 30
## PLOT 2
NUM_THREAD = 1000

# Dest IP
IP_H3 = "10.0.0.3"

# 15000 - 28 byte for header
SIZE = "14972" 

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
        # RESULT[i] = {"Timestamp":sttime, "Rtt": rtt_dict, "Output":output.stdout}
        RESULT[i] = {"Timestamp":sttime, "Rtt": rtt_dict}

        with open(LAST_PING, "w") as file:
            json.dump(RESULT[i], file)

if __name__ == "__main__":
    workers = []       

    # The DoS Attack have to start after 10 minute so we want to perfrom a 15 minute test
    t_end = time.time() + 60 * 15 # 900 s
    i = 1
    while time.time() < t_end:
    # for i in range(1, NUM_THREAD+1):
        worker = Thread(target=ping_host, args=(i,))
        workers.append(worker)
        worker.setDaemon(True)
        worker.start()
        # sleep(1/i)    # PLOT 1
        sleep(1)        # PLOT 2
        i += 1

    for w in workers:
        w.join()
    
    with open(PING_LIST, "w") as file:
        json.dump(RESULT, file)

