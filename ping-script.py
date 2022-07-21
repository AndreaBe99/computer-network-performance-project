import os
for i in range(56, 184, 64):
    response = os.popen(f"ping h2 - s " + str(i) +" - D - w 10").read()
    print("#############################################")
    print(response)
    print("#############################################")
