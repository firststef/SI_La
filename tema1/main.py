from logger import disable_logging, log
from node import Node, closeafter
from node_net import NodeNet
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


K3 = b'eu_sunt_cheia_K3'
BLOCK_SIZE = 16
ECB_BLOCK_SIZE = 32


def encrypt(message, key: bytes):
    """
    Encrypts a message using AES - CBC
    :return:
    """
    if isinstance(message, str):
        message = message.encode()
    key = pad(key, 16)
    message = pad(message, 16)
    cip = AES.new(key, AES.MODE_ECB)
    return cip.encrypt(message)


def decrypt(cr: bytes, key: bytes):
    """
    Encrypts a message using AES - CBC
    :return:
    """
    key = pad(key, 16)
    cip = AES.new(key, AES.MODE_ECB)
    return unpad(cip.decrypt(cr), 16)


def split_into_chunks(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def xor_bytestrings():pass


def ecb_encrypt(text, key: bytes, chunk_size):
    chunks = split_into_chunks(text, chunk_size)
    return [encrypt(chunk, key) for chunk in chunks]


def ecb_decrypt(chunks: list, key):
    return [decrypt(chunk, key) for chunk in chunks]


def ofb_encrypt_decrypt(text, key: bytes, chunk_size, iv):
    chunks = split_into_chunks(text, chunk_size)
    ciphertext = pad(iv, 32)
    out_chunks = []
    for chunk in chunks:
        ciphertext = encrypt(ciphertext, key)[:32]
        out_chunks.append()


class NodeA(Node):
    def __init__(self, m_o):
        super().__init__()
        self.ENCRYPTED_KEY = None
        self.SECRET_KEY = None
        self.m_o = m_o

    def who(self) -> str:
        return "A"

    def serve(self):
        log('1_ NODE A NOTIFIES B OF THE FIRST PROTOCOL')
        self.send_to("B", "establish_protocol", encrypt(self.m_o, K3))

        log('2_ NODE A REQUESTS K1/K2 FROM NODE KM')
        self.ENCRYPTED_KEY = self.request_from("KM", "get_key", encrypt("K1" if self.m_o == "ECB" else "K2", K3))

        log('5_ NODE A DECRYPTS K1 FROM KM')
        # delayed to begin phase

        log('6.5_ AFTER WE GET K1, B WILL TELL US TO BEGIN COMMUNICATION')  # SO EXECUTION MOVES TO THE BEGIN METHOD
        self.wait_one()

    @closeafter
    def begin(self):
        # from 5
        self.SECRET_KEY = decrypt(self.ENCRYPTED_KEY, K3)

        log('7_ NODE A BEGINS COMMUNICATION ')

        log('8_ NODE A ENCRYPTS A FILE USING AES AND THE ESTABLISHED M.O.')
        file = b"file12"

        log('9_ NODE A SENDS THE ENCRYPTED FILE TO B')
        self.send_to("B", "file_transfer", encrypt(file, self.SECRET_KEY), callback=None, block=0)


class NodeB(Node):
    def __init__(self):
        super().__init__()
        self.protocol = None
        self.ENCRYPTED_KEY = None
        self.SECRET_KEY = None

    def who(self) -> str:
        return "B"

    def serve(self):
        log('1.5_ WAITING FOR NODE A TO ESTABLISH PROTOCOL')
        self.wait_one()
        log('3_ NODE B REQUESTS K1 FROM NODE KM')
        self.ENCRYPTED_KEY = self.request_from("KM", "get_key", encrypt("K1" if self.protocol == "ECB" else "K2", K3))
        log('5_ NODE B DECRYPTS K1 FROM KM')
        self.begin()

    def begin(self):
        self.SECRET_KEY = decrypt(self.ENCRYPTED_KEY, K3)

        log('6_ NODE B NOTIFIES NODE A TO BEGIN COMMUNICATION')
        self.send_to("A", "begin", callback=None, block=0)

        log('9.5_ NODE B RECEIVES THE FILE FROM A')
        self.wait_one()  # or more

    @closeafter
    def establish_protocol(self, protocol):
        self.protocol = protocol

    @closeafter
    def file_transfer(self, file):
        log('10_ NODE B DECRYPTS THE FILE')
        print(decrypt(file, self.SECRET_KEY))

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
        key_t = decrypt(message, K3).decode('utf-8')
        if key_t == "K1":
            return encrypt(self.K1, K3)
        elif key_t == "K2":
            return encrypt(self.K1, K3)
        else:
            raise Exception("could not understand message")


if __name__ == '__main__':
    #disable_logging()

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
