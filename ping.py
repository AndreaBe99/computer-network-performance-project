import subprocess
import os
from time import sleep

with open(os.devnull, "wb") as limbo:
    for n in range(1, 10, 2):
        ip_h3 = "10.0.0.3".format(n)
        # if we want to ping only one ip at a time, we have to uese subprocess.call()
        ping = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip_h3],
                                stdout=subprocess.PIPE, stderr=limbo).wait()
        output = ping.communicate()
        if ping:
            print(ip_h3, "inactive")
        else:
            print(ip_h3, "active")