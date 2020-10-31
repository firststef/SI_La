import base64

from node import Node
from node_net import NodeNet


class NodeA(Node):
    def who(self) -> str:
        return "A"

    def serve(self):
        self.wait_one(lambda x: x)

    def wow(self, param):
        print("wow", base64.b64decode(param))


class NodeB(Node):
    def who(self) -> str:
        return "B"

    def serve(self):
        self.send_to("A", "wow", 'w'.encode('utf-8'))


class NodeK(Node):
    def who(self) -> str:
        return "K"

    def serve(self):
        pass


if __name__ == '__main__':
    n = NodeNet()
    a = n.create_node(NodeA)
    b = n.create_node(NodeB)
    k = n.create_node(NodeK)

    a.start()
    b.start()
