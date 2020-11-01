from logger import disable_logging, log
from node import Node, closeafter
from node_net import NodeNet


K3 = b'eu_sunt_cheia_K3'


def encrypt(message, key):
    return message


def decrypt(message, key):
    return message


class NodeA(Node):
    def __init__(self, m_o):
        super().__init__()
        self.ENCRYPTED_K1 = None
        self.K1 = None
        self.m_o = m_o

    def who(self) -> str:
        return "A"

    def serve(self):
        log('1_ NODE A NOTIFIES B OF THE FIRST PROTOCOL')
        self.send_to("B", "establish_protocol", encrypt(self.m_o, K3))
        log('2_ NODE A REQUESTS K1/K2 FROM NODE KM')
        self.ENCRYPTED_K1 = self.request_from("KM", "get_key", encrypt("K1", K3))
        log('5_ NODE A DECRYPTS K1 FROM KM')
        log('6.5_ AFTER WE GET K1, B WILL TELL US TO BEGIN COMMUNICATION')  # SO EXECUTION MOVES TO THE BEGIN METHOD
        self.wait_one()

    @closeafter
    def begin(self):
        self.K1 = decrypt(self.ENCRYPTED_K1, K3)
        log('7_ NODE A BEGINS COMMUNICATION ')

        log('8_ NODE A ENCRYPTS A FILE USING AES AND THE ESTABLISHED M.O.')

        log('9_ NODE A SENDS THE ENCRYPTED FILE TO B')
        self.send_to("B", "file_transfer", encrypt("file1", self.K1), callback=None, block=0)


class NodeB(Node):
    def __init__(self):
        super().__init__()
        self.protocol = None
        self.ENCRYPTED_K1 = None
        self.K1 = None

    def who(self) -> str:
        return "B"

    def serve(self):
        log('1.5_ WAITING FOR NODE A TO ESTABLISH PROTOCOL')
        self.wait_one()
        log('3_ NODE B REQUESTS K1 FROM NODE KM')
        self.ENCRYPTED_K1 = self.request_from("KM", "get_key", encrypt("K1", K3))
        log('5_ NODE B DECRYPTS K1 FROM KM')
        self.begin()

    def begin(self):
        self.K1 = decrypt(self.ENCRYPTED_K1, K3)

        log('6_ NODE B NOTIFIES NODE A TO BEGIN COMMUNICATION')
        self.send_to("A", "begin", callback=None, block=0)

        log('9.5_ NODE B RECEIVES THE FILE FROM A')
        self.wait_one()  # or more
        self.rpc.watchdog.stop()

    @closeafter
    def establish_protocol(self, protocol):
        self.protocol = protocol

    @closeafter
    def file_transfer(self, file):
        log('10_ NODE B DECRYPTS THE FILE')
        print(decrypt(file, self.K1))

        log('END OF COMMUNICATION')


class NodeKM(Node):
    def __init__(self):
        super().__init__()
        self.K1 = b'eu_sunt_cheia_ECB'
        self.K2 = b'eu_sunt_cheia_OFB'

    def who(self) -> str:
        return "KM"

    def serve(self):
        log('1.5_ WAITING FOR NODE A TO REQUEST K1')
        self.wait_one()
        log('3.5_ WAITING FOR NODE B TO REQUEST K1')
        self.wait_one()

    @closeafter
    def get_key(self, message):
        log('4_ NODE KM ENCRYPTS K1 OR K2 AND SENDS THEM TO THE NODES')
        return 'get_key_res'


if __name__ == '__main__':
    disable_logging()

    n = NodeNet()
    a = n.create_node(NodeA, "ECB")
    b = n.create_node(NodeB)
    km = n.create_node(NodeKM)

    a.start()
    b.start()
    km.start()

    a.join()
    b.join()
    km.join()
    exit(0)
