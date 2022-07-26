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

        # clean_net()
        info("*** Creating (reference) controllers\n")
        #c1 = self.addController('c1', port=6633)

        info("*** Creating switches\n")
        s1 = self.addSwitch('s1', protocols='OpenFlow13')
        s2 = self.addSwitch('s2', protocols='OpenFlow13')
        s3 = self.addSwitch('s3', protocols='OpenFlow13')
        s4 = self.addSwitch('s4', protocols='OpenFlow13')
        s5 = self.addSwitch('s5', protocols='OpenFlow13')

        for i in range(1,6):
            s = self.__getitem__("s"+str(i))
            s.sendCmd(f'ovs-vsctl set-controller s{i} tcp: localhost: 6633')

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
        self.addLink(s1, s4, bw=10, delay='5ms', max_queue_size=10)
        self.addLink(s2, s4, bw=10, delay='5ms', max_queue_size=10)
        self.addLink(s3, s4, bw=10, delay='5ms', max_queue_size=10)

        # Blue Link
        # Set Bandwidth to 5Mbps, Delay to 5ms, Max Queue Size to 10
        self.addLink(s3, s5, bw=5, delay='5ms', max_queue_size=10)
        self.addLink(s1, s5, bw=5, delay='5ms', max_queue_size=10)

        info("*** Starting network\n")
        self.build()

        info("*** Testing network\n")
        self.pingAll()
        self.pingAll()

        info("*** Running CLI\n")
        CLI(self)

        info("*** Stopping network\n" )
        self.stop()

    def clean_net(self):
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
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip='127.0.0.1'),
        switch=OVSSwitch,
        autoSetMacs=True)

    # Actually start the network
    net.start()

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
    mn --custom topology.py --topo mytopo
"""
topos = {'mytopo': (lambda: Topology())}