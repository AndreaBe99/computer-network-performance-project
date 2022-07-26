# Implementation of a simple network of switches, based on simple_switch_13.py
# Basic interaction between controller and switches should be handled by this script

from threading import Thread

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, arp, icmp, ipv4
from ryu.lib.packet import ether_types

from flow_reroute_app import flow_reroute_app
from network_graph import NetworkGraph


class BaseSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(BaseSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.dpids = {}

    # We set here an event to handle the first message that the switches will send when they connect to the controller.
    # When a switch connects, we also save its associated datapath object and identifier, so that we can later
    # send any kind of messages to it without waiting for PACKET_IN messages.
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        # Obtain the datapath object and save it
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.dpids[datapath.id] = datapath

        # Instantiate and send the default MISS rule for the switch (EMPTY match, so it matches with any flow)
        # so that when no flow rule for a packet is found, the packet is sent to the controller.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    # Function called when the application is ready and all the Ryu sub-tasks have been handled.
    # We launch here a separate thread to handle any application-based interaction with the OpenFlow network.
    def start(self):
        super().start()
        Thread(target=flow_reroute_app, args=[self]).start()

    # Function used wrap the FlowMod rule with the ADD command, and then send it to the given datapath.
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    # Function used to delete flows on the given datapath with the given match.
    # If no match is given, all the flows of the given datapath are deleted.
    # Note that we only delete values on table with id 0. If you need to work with multiple tables in yor application
    # it may be needed to change how this function works.
    def delete_flows(self, datapath, match=False):

        # If the given datapath is an integer, try to get that datapath from the dictionary of datapaths
        if isinstance(datapath, int) and datapath in self.dpids:
            datapath = self.dpids[datapath]
        else:
            return

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # If no match given, delete all rules by default. An EMPTY Match matches with all rules, unless you are using
        # a STRICT version of a given command.
        if not match:
            match = parser.OFPMatch()

        mod = parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_DELETE, match=match, cookie=0,
                                out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY, table_id=0)

        datapath.send_msg(mod)

    # Function used to delete a single rule with a source and a destination.
    # It's just a wrapper for the delete_flows function, with some values already set
    def delete_rule(self, datapath, src, dst):

        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_src=src, eth_dst=dst)

        self.delete_flows(datapath, match=match)

    # We set here the main function which will handle most of the packets that the switches receive.
    # What we do in this case, is, with the use of NetworkGraph, to try and find a route that the packets have to
    # take without using a FLOOD mechanism, which may not work in networks with loops.
    # Note that it is required for hosts
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):

        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        arp_prt = pkt.get_protocol(arp.arp)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        network = NetworkGraph()

        src_mac = eth.src
        dst_mac = eth.dst

        # If the destination mac is not known, but only the IP, we try to find the correct destination by looking
        # at the NetworkGraph of our network.
        # Note that hosts may be required to start a ping before appearing in our NetworkGraph, due to the way Ryu's
        # topology_API is written.
        if dst_mac == 'ff:ff:ff:ff:ff:ff' or dst_mac == '00:00:00:00:00:00':

            if not arp_prt:
                print("Packet couldn't be routed. Dropping...")
                return

            arp_dst = arp_prt.dst_ip
            arp_src = arp_prt.src_ip

            src_mac = network.get_host_by_ip(arp_src)
            dst_mac = network.get_host_by_ip(arp_dst)

            if not dst_mac:
                print("One host tried to reach another host which has not entered the network yet. Dropping packet...")
                print("Try to ping from the destination host before!")
                return

        # We obtain the first available path here
        paths = network.get_all_paths_with_ports(src_mac, dst_mac)
        if len(paths) == 0:
            return

        path = paths[0]
        
        # And we install the rule here.
        # Uncomment this line if you want the rule to be installed directly when a PACKET_IN is received.
        # Otherwise, find your ideal solution by working on the FlowRouteApp code.
        self.inst_path_rule(path, 1)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        # Find the next output port for the packet to travel to the destination, and send the packet to it.
        out_port = self.next_port(path, dpid)

        actions = [parser.OFPActionOutput(out_port)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    # Simple function which, given a path with ports and a datapath, returns the port which that datapath has to use
    # as an output, to allow the packet to travel through the given path.
    def next_port(self, path, dpid):

        for n in range(1, len(path) - 1):
            node, out_port = path[n]

            if node == dpid:
                return out_port

    # Function used to install, in one single action, all the flow rules on all the datapaths on a path, in order for
    # packets to travel through that path
    def inst_path_rule(self, path, priority):

        for n in range(1, len(path) - 1):
            node, out_port = path[n]

            datapath = self.dpids[node]
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(eth_dst=path[-1], eth_src=path[0])
            actions = [parser.OFPActionOutput(out_port)]

            self.add_flow(datapath, priority, match, actions)

    # Function used to delete all the rules associated with a given path.
    def del_path_rule(self, path):

        src, dst = (path[0], path[-1])

        for n in range(1, len(path) - 1):
            node, out_port = path[n]
            datapath = self.dpids[node]
            self.delete_rule(datapath, src, dst)

    # This function can be used to wake up a given host when the network starts, without having to ping from it.
    # You can either send a ping request directly to a known destination (dst), or enable on your machine to respond
    # to broadcast pings, and ping at the start of your application with a dst=255.255.255.255
    # If you, instead, already know all the hosts on your network before starting, just store them in a list and call
    # this method for all the known destinations.
    # If you need to craft packets in your application, this method may be a good start to understand how to craft
    # packets in Ryu.
    def send_packet(self, datapath, dst):

        pkt = packet.Packet()

        pkt.add_protocol(ethernet.ethernet(ethertype=0x0800, dst='ff:ff:ff:ff:ff:ff', src='00:00:00:00:00:00'))
        pkt.add_protocol(ipv4.ipv4(ttl=255, csum=0, dst=dst, src='10.0.0.255', proto=1, option=None))
        pkt.add_protocol(icmp.icmp(type_=icmp.ICMP_ECHO_REQUEST, code=icmp.ICMP_ECHO_REPLY_CODE, csum=0,
                                   data=icmp.echo(id_=0, seq=0, data=None)))

        ofproto = datapath.ofproto
        port = ofproto.OFPP_FLOOD
        parser = datapath.ofproto_parser

        pkt.serialize()
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)

        datapath.send_msg(out)
