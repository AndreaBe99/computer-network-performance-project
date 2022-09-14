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
from turtle import delay, home
from network_graph import NetworkGraph
import json
import os

LAST_PING = "../last_ping.json"
PING_LIST = "../ping_list.json"

# we use a global variable to count the nummber of packet 
# with an RTT > 2000, this beacuse we want to avoid to redirect
# the flow after a single delay.
REDIRECT = 0

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
		
		############# PLOT 1 #############
		########### Flow Rule ############
		# Consider a total traffic rate λ13, create a plot that shows how the
		# latency T increases by injecting an increasing rate λ13. 

		# Comment the following two lines if you don't want to set the rules
		set_green_flow_rule(app, h1, h3, 2)
		

		############# PLOT 2 #############
		#### Set Malicious Flow Rules ####
		# Use a timeline plot to show the increase in the latency T observed 
		# between H1 and H3 as a consequence of the ongoing attack.

		# Comment the following line to if you don't want obtain a delay
		set_malicious_flows(app, hm, h2)


		############# PLOT 3 #############
		########## Redirection ###########
		# Use another timeline plot to show the system behavior when it first 
		# discovers the attack and later reacts to it by redirecting the flow along p2.

		# Comment the following line to if you don't want obtain a redicretion
		# read_rtt_h1(app, h1, h3, 2)


		############# PLOT 4 #############
		############ Revovery ############
		# If hm is blocked we can restore the first path
		"""
		if app.drop_hm_packet:
			set_green_flow_rule(app, h1, h3, 10)
			print("#"*55)
			print("Restored Default Path")
			print("#"*55)
		"""
		# Delete all the flows from the first datapath found in the dictionary:
        #if len(app.dpids) > 0:
        #    first_entry = list(app.dpids.keys())[0]
        #    app.delete_flows(app.dpids[first_entry])

		sys.stdout.flush()
		sleep(5)

def set_green_flow_rule(app, h1, h3, priority):
	# If host 1 and host are up, we get their MAC Address and we set the paths
	if h1 and h3:
		#### h1 --> h3 ####
		src_mac = h1["mac"]
		dst_mac = h3["mac"]
		path = [src_mac, S1_PORT_H1_TO_H3, S4_PORT_H1_TO_H3, S3_PORT_H1_TO_H3, dst_mac]
		# Add rule with priority equal to 2
		app.inst_path_rule(path, priority)
		
		#### h3 --> h1 ####
		src_mac = h3["mac"]
		dst_mac = h1["mac"]
		path = [src_mac, S1_PORT_H3_TO_H1, S4_PORT_H3_TO_H1, S3_PORT_H3_TO_H1, dst_mac]
		# Add rule with priority equal to 2
		app.inst_path_rule(path, priority)


# We use the priority field in the flow rules to generate multiple 
# rules for the same pair of communicating hosts.
def set_malicious_flows(app, hm, h2):
	if hm and h2:
		# Default Path: hm --> h2 
		path = [hm["mac"], (4,1), (2,1), h2["mac"]]

		# Set 10 identical flow rules with different priority to get a delay.
		for i in range(1, 20):
			app.inst_path_rule(path, i)

	# To simulate a Dos Attack hm would have to send flows
	# with increasing size and/or frequency, until a certain 
	# value is reached wich involves the drop of some of the flows passing by for s4.

	# To do this we use another python script to execute ping from hm

def read_rtt_h1(app, h1, h3, priority):
	global REDIRECT
	# We have already applied the flow route, we can exit
	if REDIRECT > 3:
		return

	# If we have 3 delay we apply the new flow route
	if REDIRECT > 2:
		# Have the controller block the maliciuos traffic after the redirection 
		# and dynamically re-establish the more convenient route along path p1. 
		# Set the variable to drop packet from hm
		app.drop_hm_packet = True		# Comment this line to avoid to block hm

		# Set new path rule
		path = [h1["mac"], (1,3), (5,2), (3,3), h3["mac"]]
		app.inst_path_rule(path, priority)
		print("#"*55)
		print("Attack Detection: path redirection on H1->S1->S5->S3->H3")
		print("#"*55)
		

	# We check the RTT from the file
	if os.path.exists(LAST_PING):
		with open(LAST_PING, "r") as file:
			ping = json.load(file)

		print("#"*55)
		print("Time: ", ping["Timestamp"], " RTT: ", ping["Rtt"]["avg"])
		print("#"*55)
		if float(ping["Rtt"]["avg"]) > 2000:
			REDIRECT += 1

		
if __name__ == "__main__":
	print("This script is not meant to be run directly.")
	print("If you see this message, however, it means that your script has no syntax errors! :)")
