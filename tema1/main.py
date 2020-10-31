import base64

from node import Node, closeafter
from node_net import NodeNet


class NodeA(Node):
    def who(self) -> str:
        return "A"

    def serve(self):
        self.wait_one(lambda x: x)
        self.wait_one(lambda x: x)

    @closeafter
    def wow(self, param):
        print("wow", param)
        return 1


class NodeB(Node):
    def who(self) -> str:
        return "B"

    def serve(self):
        self.send_to("A", "wow", 'w')
        self.send_to("A", "wow", 'w')


class NodeKM(Node):
    def who(self) -> str:
        return "K"

    def serve(self):
        pass


if __name__ == '__main__':
    n = NodeNet()
    a = n.create_node(NodeA)
    b = n.create_node(NodeB)
    k = n.create_node(NodeKM)

    a.start()
    b.start()
