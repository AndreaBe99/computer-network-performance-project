import subprocess
import os
import ipaddress
import time
from time import sleep
from threading import Thread
from unicodedata import name
import os 

# first we get the current timestamp
T_NOW = time.time()
print("Timestamp: ", T_NOW)
IP_H3 = "10.0.0.3"
FILE_NAME = "ping_output.txt"
THREADS = []

def ping_host(i):
    output = subprocess.run(["ping", "-c", "1", "-s", "15000", IP_H3], stdout=subprocess.PIPE, encoding="utf-8")
    print(output.stdout)
    with open(FILE_NAME, "a+") as file:
        file.write(output.stdout)
        file.write("\n")


if __name__ == "__main__":
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
        with open(FILE_NAME, 'w') as f:
            pass
  
    for i in range(1,10,2):
        thread = Thread(target=ping_host, args=(i,))
        THREADS.append(thread)
        thread.start()
        sleep(60)
    
    for t in THREADS:
        t.join()