from mininet.cli import CLI
from mininet.node import Controller, OVSSwitch
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch, RemoteController
from mininet.log import setLogLevel, info
from subprocess import Popen


class Topology(Topo):
    def __init__(self):
        """ init topology """
        Topo.__init__(self)
        "Create a network from semi-scratch with multiple controllers."

        info("*** Creating switches\n")
        s1 = self.addSwitch('s1', protocols='OpenFlow13')
        s2 = self.addSwitch('s2', protocols='OpenFlow13')
        s3 = self.addSwitch('s3', protocols='OpenFlow13')
        s4 = self.addSwitch('s4', protocols='OpenFlow13')
        s5 = self.addSwitch('s5', protocols='OpenFlow13')

        info("*** Creating hosts\n")
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        hm = self.addHost('hm')

        info("*** Creating links\n")
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s3)
        self.addLink(hm, s4)

        # Green Link
        # Set Bandwidth to 10Mbps, Delay to 5ms, Max Queue Size to 10
        self.addLink(s1, s4, bw=10, delay='0.1ms', max_queue_size=10)
        self.addLink(s2, s4, bw=10, delay='0.1ms', max_queue_size=10)
        self.addLink(s3, s4, bw=10, delay='0.1ms', max_queue_size=10)

        # Blue Link
        # Set Bandwidth to 5Mbps, Delay to 5ms, Max Queue Size to 10
        self.addLink(s3, s5, bw=5, delay='5ms', max_queue_size=10)
        self.addLink(s1, s5, bw=5, delay='5ms', max_queue_size=10)

def clean_net():
    """Clean mininet to allow to create new topology"""
    info('*** Clean net\n')
    cmd = "mn -c"
    Popen(cmd, shell=True).wait()


def run_topology():
    "Bootstrap a Mininet network using the Topology"

    # Create an instance of our topology
    topo = Topology()

    # Create a network based on the topology using OVS and controlled by
    # a remote controller.
    net = Mininet( topo=topo,
                   build=False,
                   ipBase='10.0.0.0/24')

    # Actually start the network
    net.build()

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    switch_list = ["s1", "s2", "s3", "s4", "s5"]
    for switch in switch_list:
        net.get(switch).start([])
        net.get(switch).cmdPrint("ovs-vsctl set-controller {} tcp:6633".format(switch))
    
    info("*** Testing network\n")
    net.pingAll()
    net.pingAll()

    # Drop the user in to a CLI so user can run commands.
    CLI(net)

    # After the user exits the CLI, shutdown the network.
    net.stop()


if __name__ == '__main__':
    """
    This runs if this file is executed directly:
        sudo python3 topology.py
    """
    setLogLevel('info')
    run_topology()

"""
Allows the file to be imported using:
    sudo mn --custom topology.py --controller remote --switch ovsk --topo mytopo
"""
topos = {'mytopo': (lambda: Topology())}