from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.link import Link, TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

def customTopo():
    net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)
   
    net.addController('c0')

    s1 = net.addSwitch('s1')  
    s2 = net.addSwitch('s2')  
    s3 = net.addSwitch('s3')  
    
    net.addLink(s1, s2)  
    net.addLink(s1, s3)

    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    net.addLink(h1, s1)
    net.addLink(h2, s2)

    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    net.addLink(h3, s3)
    net.addLink(h4, s3)



    net.start()

    # Configure multicast snooping on all switches
    for switch in [s1, s2, s3]:
        switch.cmd('ovs-vsctl set Bridge {} other-config:mcast-snooping-querier=true'.format(switch.name))
        switch.cmd('ovs-ofctl add-flow {} "table=0, priority=99, ipv6, nw_dst=*, actions=normal"'.format(switch.name))
        switch.cmd('ovs-vsctl set Bridge {} mcast_snooping_enable=true'.format(switch.name))
        switch.cmd('ovs-vsctl set Bridge {} other-config:mcast-snooping-disable-flood-unregistered=true'.format(switch.name))
        switch.cmd('ovs-vsctl set Port {}-eth1 other-config:mcast-snooping-flood-reports=true'.format(switch.name))
        
        
   # switch.cmd('ovs-ofctl add-flow s1 "table=0, priority=99, ipv6, nw_dst=*, actions=normal"')

	
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTopo()

