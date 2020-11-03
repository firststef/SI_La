class NodeDNS:
    def __init__(self):
        self.record = {}

    def get_address_for(self, node_name):
        return self.record[node_name]

    def register_node(self, node_name, address):
        if node_name in self.record:
            raise Exception("This server is already registered")
        self.record[node_name] = address

    def inc(self, node_name):
        self.record[node_name] = (self.record[node_name][0], self.record[node_name][1] + 3)
