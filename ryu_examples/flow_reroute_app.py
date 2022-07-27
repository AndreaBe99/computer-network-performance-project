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
from turtle import home
from network_graph import NetworkGraph

HOST_NUMBER = 4

"""
	#### PORT MAC ####
	# If the port all always the same
	#  host : port --> port : host
	h1 : ? --> 1 : s1
	s1 : 2 --> 2 : s4
	s4 : 3 --> 2 : s3
	s3 : 3 --> ? : h3
"""

#### h1 --> h3 ####
S1_PORT_H1_TO_H3 = (1, 2)
S3_PORT_H1_TO_H3 = (3, 3)
S4_PORT_H1_TO_H3 = (4, 3)

#### h3 --> h1 ####
S1_PORT_H3_TO_H1 = (1, 1)
S3_PORT_H3_TO_H1 = (3, 2)
S4_PORT_H3_TO_H1 = (4, 2)

# (switch_number, exit_port)

def flow_reroute_app(app):
	while True:
		while True:
			try:
				network = NetworkGraph()
				break
			except:
				pass
		
		h1, h2, h3, hm = None, None, None, None
		# Check if all the hosts are connected 
		if len(network.hosts) == HOST_NUMBER:
			hosts = network.hosts
			for host in hosts:
				port_name = host["port"]["name"]
				# Check if it is connected to s1 switch, because h1 is connected with s1
				# We can do the same checking dpid equal to 1 or 3, instead of 'port_name'
				# Check if IP is assigned
				if "s1" in port_name and host["ipv4"] != []:
					h1 = host
				if "s3" in port_name and host["ipv4"] != []:
					h3 = host

				# For Dos Attack
				if "s4" in port_name and host["ipv4"] != []:
					hm = host
				if "s2" in port_name and host["ipv4"] != []:
					h2 = host
		
		#### Flow Rule Plot 1 ####
		# If host 1 and host are up, we get their MAC Address and we set the paths
		if h1 and h3:
			#### h1 --> h3 ####
			src_mac = h1["mac"]
			dst_mac = h3["mac"]
			path = [src_mac, S1_PORT_H1_TO_H3, S4_PORT_H1_TO_H3, S3_PORT_H1_TO_H3, dst_mac]
			# Add rule with priority equal to 2
			app.inst_path_rule(path, 2)
			
			#### h3 --> h1 ####
			src_mac = h3["mac"]
			dst_mac = h1["mac"]
			path = [src_mac, S1_PORT_H3_TO_H1, S4_PORT_H3_TO_H1, S3_PORT_H3_TO_H1, dst_mac]
			# Add rule with priority equal to 2
			app.inst_path_rule(path, 2)
		
		#### Set Malicious Flow Rules ####
		# Uncomment the following two line to obtain a delay
		#if hm and h2:
		#	set_malicious_flows(app, hm, h2)

		# Delete all the flows from the first datapath found in the dictionary:
        #if len(app.dpids) > 0:
        #    first_entry = list(app.dpids.keys())[0]
        #    app.delete_flows(app.dpids[first_entry])

		sys.stdout.flush()
		sleep(5)

# We use the priority field in the flow rules to generate multiple 
# rules for the same pair of communicating hosts.
def set_malicious_flows(app, hm, h2):

	# Default Path: hm --> h2 
	path = [hm["mac"], (4,1), (2,1), h2["mac"]]

	# Set 10 identical flow rules with different priority to get a delay.
	for i in range(1, 10):
		app.inst_path_rule(path, i)

	# To simulate a Dos Attack hm would have to send flows
	# with increasing size and/or frequency, until a certain 
	# value is reached wich involves the drop of some of the flows passing by for s4.

	# To do this we use another python script to execute ping from hm
		
if __name__ == "__main__":
	print("This script is not meant to be run directly.")
	print("If you see this message, however, it means that your script has no syntax errors! :)")
