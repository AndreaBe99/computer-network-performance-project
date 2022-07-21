import requests
import networkx as nx
import matplotlib.pyplot as plot


class NetworkGraph:

    def __init__(self):

        switches = requests.get("http://localhost:8080/v1.0/topology/switches")
        links = requests.get("http://localhost:8080/v1.0/topology/links")
        hosts = requests.get("http://localhost:8080/v1.0/topology/hosts")

        self.switches = switches.json()
        self.links = links.json()
        self.hosts = hosts.json()

        graph = nx.DiGraph()

        for s in self.switches:
            dpid = to_dec(s["dpid"])
            graph.add_node(dpid)

        for l in self.links:
            src = to_dec(l["src"]["dpid"])
            dst = to_dec(l["dst"]["dpid"])

            port_src = to_dec(l["src"]["port_no"])
            port_dst = to_dec(l["dst"]["port_no"])

            graph.add_edge(src, dst, port_src=port_src, port_dst=port_dst)


        for h in self.hosts:
            # we set the id of the host's node to be its ipv4 address
            h_id = h["mac"]
            h_ip = host_ip(h)
            h_dpid = to_dec(h["port"]["dpid"])
            h_port = to_dec(h["port"]["port_no"])

            # if no ip is associated with the host, we don't add it to the network
            if h_ip == "0.0.0.0":
                continue

            # for each host, we also add an edge which connects it to its switch,
            # note that for this link, only one port is defined (the hosts don't
            # have port numbers for their interfaces), so we assign both ports to the same
            # number to handle easily some cases in the pathing later
            graph.add_node(h_id, ip=h_ip)
            graph.add_edge(h_dpid, h_id, port_src=h_port, port_dst=h_port)
            graph.add_edge(h_id, h_dpid, port_src=h_port, port_dst=h_port)

        self.graph = graph

    def get_host_by_ip(self, ip):

        nodes = self.graph.nodes(data=True)
        for n in nodes:

            if n[1] == {}:
                continue

            n_mac = n[0]
            n_ip = n[1]["ip"]

            if n_ip == ip:
                return n_mac

        return False

    def get_all_paths_with_ports(self, src, dst):
    
        # Get the path from source to destination, with a port for each hop!
        # Tips: use networkx.all_shortest_paths()

        if not self.graph.has_node(src) or not self.graph.has_node(dst):
            return []

        paths = nx.all_shortest_paths(self.graph, src, dst)

        paths_res = []
        for path in paths:

            path_temp = [src]
            for n in range(1, len(path)-1):
                n1 = path[n]
                n2 = path[n+1]
                ports = self.graph.get_edge_data(n1, n2)
                out_port = ports["port_src"]
                path_temp.append((n1, out_port))

            path_temp.append(dst)

            paths_res.append(path_temp)

        return paths_res


# Simple function used to convert hexadecimal numbers to integer strings,
# used by the application mainly for parsing datapath ids and port numbers
def to_dec(hex):
    return int(hex, 16)


# Function used for finding hosts ip. Mainly needed because sometimes
# hosts may have multiple ips assigned, and we only want to get one
# If you encounter problems with this ip assignment, try to check
# http://localhost:8080/v1.0/topology/hosts
# see what IPs your hosts have, and modify this function accordingly.
def host_ip(host):

    h_ip = "0.0.0.0"

    for ip in host["ipv4"]:

        if ip == "0.0.0.0":
            continue
        else:
            h_ip = ip
            break

    return h_ip


if __name__ == "__main__":

    network = NetworkGraph()

    edges = network.graph.edges


    # once the network graph is created, we try a simple pathing from one
    # host to another to see if everything works
    path_0 = network.get_all_paths_with_ports(
        network.get_host_by_ip("10.0.0.1"),
        network.get_host_by_ip("10.0.0.2")
        )


    path_1 = network.get_all_paths_with_ports(
        network.get_host_by_ip("10.0.0.2"),
        network.get_host_by_ip("10.0.0.1")
        )


    print(path_0)
    print(path_1)






