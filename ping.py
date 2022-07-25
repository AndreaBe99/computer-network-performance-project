from concurrent.futures import thread
import subprocess
import os
import time
from time import sleep
from threading import Thread
from unicodedata import name

# first we get the current timestamp
t_now = time.time()
print("Timestamp: ", t_now)

num_threads = 10

def ping_host():
    with open(os.devnull, "wb") as limbo:
        for n in range(1,10,2):
            ip_h3 = "10.0.0.3".format(n)
            # if we want to ping only one ip at a time, we have to uese subprocess.call()
            while(t_now < t_now + 60):
                ping = subprocess.Popen(["ping", "-c", "1", "-s", "15000", ip_h3],
                                        stdout=subprocess.PIPE, stderr=limbo).wait()
                output = ping.communicate()
        # wait 1 sec in between each thread
        sleep(1)

if name == "__main__":
    for i in range(num_threads):
        thread = Thread(target=ping_host, args=num_threads)
        thread.start()
        thread.join()
        print("thread finishing...exiting")