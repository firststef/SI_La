from node import Node
from node_net_dns import NodeDNS
from typing import Type, TypeVar

TNode = TypeVar("TNode", bound=Node)


class NodeNet:
    def __init__(self):
        self.dns = NodeDNS()
        self.port_range = [p for p in range(23000, 23003)]

    def create_node(self, node_type: Type[TNode]) -> TNode:
        port = self.port_range.pop(0)
        if not port:
            raise IndexError("Could not assign new node port")
        node = node_type()
        self.dns.register_node(node.who(), ('127.0.0.1', port))
        node.register_dns(self.dns)
        return node
