# This function should handle all the main logic of the application.
# It is scheduled on a separate thread by BaseSwitch.start() so that the main controller application can run
# independently of the main loop described here.

# Not that, differently from what it was shown in the last lecture, flow rule installation is not handled any more by 
# packet-in messages. This is because flow rule installation should be defined depending on application-controlled
# decisions.
# BaseSwitch will handle packet-in to redirect messages without flow-rules installed, but rtt will be very high.
# The methods for rule installation and deletion are still present and ready to be used for your application.

import sys
from time import sleep
from network_graph import NetworkGraph

SWITCH_NUMBER = 5
HOST_NUMBER = 4

def flow_reroute_app(app):
	hosts = {}
	switches = {}

	while True:
		# An example on how to interact with the Ryu Application
		#print(app.dpids.keys())
		while True:
			try:
				network = NetworkGraph()
				break
			except:
				pass
		
		if len(network.hosts) == HOST_NUMBER:
			hosts = network.hosts
			print(hosts)
		if len(network.switches) == SWITCH_NUMBER:
			switches = network.switches
			print(switches)
		
		
		sys.stdout.flush()
		# (MAC, 1)
		# app.inst_path_rule(path, priority)
		# Delete all the flows from the first datapath found in the dictionary:
		#if len(app.dpids) > 0:
		#    first_entry = list(app.dpids.keys())[0]
		#    app.delete_flows(app.dpids[first_entry])
		sleep(5)
		
if __name__ == "__main__":
	print("This script is not meant to be run directly.")
	print("If you see this message, however, it means that your script has no syntax errors! :)")
