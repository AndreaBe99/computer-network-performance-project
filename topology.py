from mininet.cli import CLI
from mininet.node import Controller, OVSSwitch
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch, RemoteController
from mininet.log import setLogLevel, info

def set_topology():
    "Create a network from semi-scratch with multiple controllers."

    net = Mininet(controller=Controller, switch=OVSSwitch, waitConnected=True)

    info("*** Creating (reference) controllers\n")
    c1 = net.addController('c1', port=6633)

    info("*** Creating switches\n")
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')
    s3 = net.addSwitch('s3', protocols='OpenFlow13')
    s4 = net.addSwitch('s4', protocols='OpenFlow13')
    s5 = net.addSwitch('s5', protocols='OpenFlow13')
    switch_list = [s1, s2, s3, s4, s5]

    info("*** Creating hosts\n")
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    hm = net.addHost('hm')

    info("*** Creating links\n")
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s3)
    net.addLink(hm, s4)

    # Green Link
    # Set Bandwidth to 10Mbps, Delay to 5ms, Max Queue Size to 10
    net.addLink(s1, s4, bw=10, delay='5ms', max_queue_size=10)
    net.addLink(s2, s4, bw=10, delay='5ms', max_queue_size=10)
    net.addLink(s3, s4, bw=10, delay='5ms', max_queue_size=10)

    # Blue Link
    # Set Bandwidth to 5Mbps, Delay to 5ms, Max Queue Size to 10
    net.addLink(s3, s5, bw=5, delay='5ms', max_queue_size=10)
    net.addLink(s1, s5, bw=5, delay='5ms', max_queue_size=10)

    info("*** Starting network\n")
    net.build()
    c1.start()
    s1.start([c1])

    info("*** Testing network\n")
    net.pingAll()

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n" )
    net.stop()

if __name__ == '__main__':
    """
    Use this script to set the topology.
    From Console: sudo python3 topology.py
    """
    setLogLevel('info')  # for CLI output
    set_topology()
