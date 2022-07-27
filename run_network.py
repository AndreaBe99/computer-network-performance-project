#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/24')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    hm = net.addHost('hm', cls=Host, ip='10.0.0.4', defaultRoute=None)

    info( '*** Add links\n')
    h1s1 = {'bw':5,'delay':'5','max_queue_size':10}
    net.addLink(h1, s1, cls=TCLink , **h1s1)
    h2s2 = {'bw':5,'delay':'5','max_queue_size':10}
    net.addLink(h2, s2, cls=TCLink , **h2s2)
    s2s4 = {'bw':10,'delay':'5','max_queue_size':10}
    net.addLink(s2, s4, cls=TCLink , **s2s4)
    s1s4 = {'bw':10,'delay':'5','max_queue_size':10}
    net.addLink(s1, s4, cls=TCLink , **s1s4)
    s1s5 = {'bw':5,'delay':'5','max_queue_size':10}
    net.addLink(s1, s5, cls=TCLink , **s1s5)
    s5s3 = {'bw':5,'delay':'5','max_queue_size':10}
    net.addLink(s5, s3, cls=TCLink , **s5s3)
    s4s3 = {'bw':10,'delay':'5','max_queue_size':10}
    net.addLink(s4, s3, cls=TCLink , **s4s3)
    s3h3 = {'bw':5,'delay':'5','max_queue_size':10}
    net.addLink(s3, h3, cls=TCLink , **s3h3)
    s4hm = {'bw':5,'delay':'5','max_queue_size':10}
    net.addLink(s4, hm, cls=TCLink , **s4hm)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([])
    net.get('s2').start([])
    net.get('s3').start([])
    net.get('s4').start([])
    net.get('s5').start([])

    info( '*** Post configure switches and hosts\n')
    s1.cmdPrint('ovs-vsctl set-controller s1 tcp:localhost:6633')
    s2.cmdPrint('ovs-vsctl set-controller s2 tcp:localhost:6633')
    s3.cmdPrint('ovs-vsctl set-controller s3 tcp:localhost:6633')
    s4.cmdPrint('ovs-vsctl set-controller s4 tcp:localhost:6633')
    s5.cmdPrint('ovs-vsctl set-controller s5 tcp:localhost:6633')

    info("*** Testing network\n")
    net.pingAll()
    net.pingAll()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

