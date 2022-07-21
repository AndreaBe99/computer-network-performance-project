import requests
import networkx as nx
import matplotlib.pyplot as plot

if __name__ == "__main__":
    switches = requests.get("http://localhost:8080/v1.0/topology/switches").json()
    links = requests.get("http://localhost:8080/v1.0/topology/links").json()
    hosts = requests.get("http://localhost:8080/v1.0/topology/hosts").json()

    network = nx.Graph()

    for s in switches:
        network.add_node(s["dpid"])

    for l in links:
        src = l["src"]["dpid"]
        dst = l["dst"]["dpid"]
        network.add_edge(src, dst)

    for h in hosts:
        pass

    draw = nx.draw(network)
    plot.show()