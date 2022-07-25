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

SWITCH_NUMBER = 5
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
# (switch_number, exit_port)
S1_PORT = (1, 2)
S3_PORT = (3, 3)
S4_PORT = (4, 3)

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
			print("HOST: ", hosts)

		if len(network.switches) == SWITCH_NUMBER:
			switches = network.switches
			print("SWITCH: ", switches)
		
		if network.hosts and network.switches:
			# We need h1 and h3 MAC
			h1, h3 = None, None
			for host in hosts:
				port_name = host["port"]["name"]
				# Check if is s1 switch, because h1 is connected with s1
				if "s1" in port_name:
					h1 = host
				# Check if is s3 switch, because h3 is connected with s3
				if "s3" in port_name:
					h3 = host
				# We can do the same checking dpid equal to 1 or 3
			
			# We need s1, s4 and s3 MAC
			# For now is not necessary
			"""
			s1, s3, s4 = None, None, None
			for switch in switches:
				dpid = int(switch["dpid"])
				
				if dpid == 1:
					s1 = switch
				if dpid == 3:
					s3 = switch
				if dpid == 4:
					s3 = switch
			"""
			src_mac = h1["mac"]
			dst_mac = h3["mac"]
			"""
				#### Path structure ####
				[src_mac, (switch, exit_port), (switch, exit_port), ..., dst_mac]
			"""
			path = []
			path.append(src_mac)
			path.append(S1_PORT)
			path.append(S4_PORT)
			path.append(S3_PORT)
			path.append(dst_mac)


			# Add rule with priority equal to 2
			app.inst_path_rule(path, 2)
			
			print("##################################")
			print("ADD: ", path)
			print("##################################")

	
		sys.stdout.flush()
		# Delete all the flows from the first datapath found in the dictionary:
		#if len(app.dpids) > 0:
		#    first_entry = list(app.dpids.keys())[0]
		#    app.delete_flows(app.dpids[first_entry])
		sleep(5)
		
if __name__ == "__main__":
	print("This script is not meant to be run directly.")
	print("If you see this message, however, it means that your script has no syntax errors! :)")
