import subprocess
import os
import time
from threading import Thread

# first we get the current timestamp
t_now = time.time()
print("Timestamp: ", t_now)

with open(os.devnull, "wb") as limbo:
    for n in range(1, 10, 2):
        ip_h3 = "10.0.0.3".format(n)
        # if we want to ping only one ip at a time, we have to uese subprocess.call()
        while(t_now < t_now + 60):
            ping = subprocess.Popen(["ping", "-c", "1", "-s", "15000", ip_h3],
                                    stdout=subprocess.PIPE, stderr=limbo).wait()
            output = ping.communicate()