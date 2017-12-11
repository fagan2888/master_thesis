from __future__ import print_function 
import re
import os
import ipaddr as ip
from collections import defaultdict


ROUTES_FILE = '/home/mininet/miniNExT/util/routes.txt'
ROUTER_CONF = '/home/mininet/miniNExT/examples/master_thesis/project/configs/interfaces'


class Net:

    def __init__(self):
        self.destinations=set()
        self.routers=set()
        # contains the networks to which the routers is directly connected [probably useless]
        self.connected_networks = defaultdict(list)
        # map each router to its list of addresses
        self.addresses = defaultdict(list)
        # map each address to the router
        self.addr_rout = defaultdict()
        # contains the routing information: dst->next_hop
        self.routes = defaultdict(dict)
    

    def parse_routes(self, routes_file, addr_file):
        # getting routers routing tables
        with open(routes_file, 'r') as f:
	    for line in f:
	        line = line.strip()
	        if line:
	            router, network, next_hop = line.split()
	            self.routers.add(router)
	               
	            if Net._is_same_network(next_hop):
	                self.connected_networks[router].append(network)
	            self.routes[router][network] = next_hop
	
	# getting routers address configuration
        with open(addr_file, 'r') as f:
            for line in f:
	        line = line.strip()
	        if line:
                    router, interface, address = line.split()
                    self.addresses[router].append(address)
	            self.destinations.add(address)
	    
	self.routers = sorted(self.routers)
        #connected_routers = invert_dict(connected_networks, type='list')
        self.addr_rout=invert_dict(self.addresses)
        self.get_path('r1', '172.168.4.2')
	

    def get_path(self, src_router, dst_addr):
        next_hop = self.routes[src_router][Net._addr_to_net(dst_addr)]
        path = [src_router]
        while next_hop!='0.0.0.0':
                src_router=self.addr_rout[next_hop]
                next_hop = self.routes[src_router][Net._addr_to_net(dst_addr)]
                path.append(src_router)
       
        # it is possible to reach an ip through another interface, need to double check
        last = self.addr_rout[dst_addr]
        if last != path[-1]:
            path.append(self.addr_rout[dst_addr])
        Net._print_path(path)
        path = [self.routers.index(hop)  for hop in path]
        # returning path in terms of hop index
        return path
    

    @staticmethod
    def _print_path(path):
        print(path[0], end=' ')
        for hop in path[1:]:
            print('-> ' + hop, end=' ')
        print()


    # all my networks are /24, not a proper implementet method, just putting a 0 instead of the host
    @staticmethod 
    def _addr_to_net(addr, prefix=24):
        return re.sub("([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+", "\\1.0", addr)
    
    @staticmethod 
    def _is_same_network(next_hop):
        return next_hop=='0.0.0.0'
    

def invert_dict(dic, type=None):
    if type == 'list':
        return _invert_dict_list(dic)
    return _invert_dict(dic)
    

# if there's only one value per key
def _invert_dict(dic):
    inverted = defaultdict()

    for k,v in dic.items():
        for item in v:
            inverted[item]=k
    return dict(inverted)


# if there are multiple values for the same key
def _invert_dict_list(dic):
    inverted = defaultdict(list)
    
    for k,v in dic.items():
        for item in v:
            inverted[item].append(k)
    return dict(inverted)


if __name__=='__main__':
    net = Net()
    net.parse_routes(ROUTES_FILE, ROUTER_CONF)
