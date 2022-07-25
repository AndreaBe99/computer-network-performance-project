import subprocess
import os
import ipaddress
import time
from time import sleep
from threading import Thread
from unicodedata import name

# first we get the current timestamp
t_now = time.time()
print("Timestamp: ", t_now)

ip_h3 = ipaddress.ip_address('10.0.0.3')

def ping_host():
    with open(os.devnull, "wb") as limbo:
        while(t_now < t_now + 60):   
        # if we want to ping only one ip at a time, we have to uese subprocess.call()
            ping = subprocess.Popen(["ping", "-c", "1", "-s", "15000", ip_h3],
                            stdout=subprocess.PIPE, stderr=limbo).wait()
            # we use communicate method to store the output of the command in a string
            output = ping.communicate()[0]
            print(output)

def ping_thread():
    for i in range(1,10,2):
        thread = Thread(target=ping_host, args=i)
        thread.start()
        thread.join()
        # wait 1 sec in between each thread
        sleep(1)