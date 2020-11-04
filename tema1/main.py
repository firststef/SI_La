from logger import disable_logging, log
import lspy
from node import Node, closeafter
from node_net import NodeNet
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


K3 = b'eu_sunt_cheia_K3'  # K3 is public to A, B, KM
BLOCK_SIZE = 16
ECB_BLOCK_SIZE = 32
OFB_BLOCK_SIZE = 32
IV = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
PROTOCOL_ECB = b'ECB'
PROTOCOL_OFB = b'OFB'

# ENCRYPTION FUNCTIONS -----------------------------------------------------------------------------------------------


def encrypt(message, key: bytes):
    """ Encrypts a message using AES - CBC """
    if isinstance(message, str):
        message = message.encode()
    key = pad(key, 16)
    message = pad(message, 16)
    cip = AES.new(key, AES.MODE_ECB)
    return cip.encrypt(message)


def decrypt(cr: bytes, key: bytes):
    """ Decrypts a message using AES - CBC """
    key = pad(key, 16)
    cip = AES.new(key, AES.MODE_ECB)
    return unpad(cip.decrypt(cr), 16)


def split_into_chunks(text, chunk_size):
    """ Splits the text into pieces of the same size """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def xor_bytestrings(str1, str2):
    """ Apply xor to bytestrings """
    return bytes(aa ^ bb for aa, bb in zip(str1, str2))


def ecb_encrypt(text, key: bytes, chunk_size):
    pad(text, chunk_size)
    chunks = split_into_chunks(text, chunk_size)
    encrypted_chunks = [encrypt(chunk, key) for chunk in chunks]
    return b''.join(encrypted_chunks), len(encrypted_chunks[0])


def ecb_decrypt(file, key, chunk_size):
    chunks = split_into_chunks(file, chunk_size)
    return b''.join([decrypt(chunk, key) for chunk in chunks])


def ofb_encrypt_decrypt(text, key: bytes, chunk_size, iv):
    chunks = split_into_chunks(text, chunk_size)
    ciphertext = pad(iv, OFB_BLOCK_SIZE)
    out_chunks = []
    for chunk in chunks:
        ciphertext = encrypt(ciphertext, key)[:OFB_BLOCK_SIZE]
        out_chunks.append(xor_bytestrings(ciphertext, chunk))
    return b''.join(out_chunks), len(out_chunks[0])

# NODES --------------------------------------------------------------------------------------------------------------


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
        self.ENCRYPTED_KEY = self.request_from("KM", "get_key", encrypt("K1" if self.m_o == PROTOCOL_ECB else "K2", K3))

        log('5_ NODE A DECRYPTS K1 FROM KM')
        # delayed to begin phase

        log('6.5_ AFTER WE GET K1, B WILL TELL US TO BEGIN COMMUNICATION')  # SO EXECUTION MOVES TO THE BEGIN METHOD
        self.wait_one()

    @closeafter
    def begin(self):
        """ This method starts the communication with B for transferring the file """
        # from 5
        self.SECRET_KEY = decrypt(self.ENCRYPTED_KEY, K3)

        log('7_ NODE A BEGINS COMMUNICATION ')

        log('8_ NODE A ENCRYPTS A FILE USING AES AND THE ESTABLISHED M.O.')
        file = open('files/a.txt', 'rb').read()

        log('9_ NODE A SENDS THE ENCRYPTED FILE TO B')
        if self.m_o == PROTOCOL_ECB:
            self.send_to("B", "file_transfer", *ecb_encrypt(file, self.SECRET_KEY, ECB_BLOCK_SIZE), callback=None, block=0)
        else:
            self.send_to("B", "file_transfer", *ofb_encrypt_decrypt(file, self.SECRET_KEY, OFB_BLOCK_SIZE, IV), callback=None, block=0)


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
        self.ENCRYPTED_KEY = self.request_from("KM", "get_key", encrypt("K1" if self.protocol == PROTOCOL_ECB else "K2", K3))

        log('5_ NODE B DECRYPTS K1 FROM KM')
        self.SECRET_KEY = decrypt(self.ENCRYPTED_KEY, K3)

        log('6_ NODE B NOTIFIES NODE A TO BEGIN COMMUNICATION')
        self.send_to("A", "begin", callback=None, block=0)

        log('6.5_ NODE B WAITS THE FILE FROM A')
        self.wait_one()  # or more

    @closeafter
    def establish_protocol(self, protocol):
        """ This method saves the chosen mode of encryption for transferring the file """
        self.protocol = decrypt(protocol, K3)

    @closeafter
    def file_transfer(self, file, chunk_size):
        """ This method receives the file from node A in an encrypted form and as a parameter"""
        log('10_ NODE B DECRYPTS THE FILE')
        if self.protocol == PROTOCOL_ECB:
            print("FINAL RESULT: ", ecb_decrypt(file, self.SECRET_KEY, chunk_size))
        elif self.protocol == PROTOCOL_OFB:
            print("FINAL RESULT: ", ofb_encrypt_decrypt(file, self.SECRET_KEY, OFB_BLOCK_SIZE, IV))
        else:
            raise Exception("Protocol is invalid")

        log('END OF COMMUNICATION')
        exit(0)


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
        """ This method retrieves the keys for the nodes from the key manager """
        log('4_ NODE KM ENCRYPTS K1 OR K2 AND SENDS THEM TO THE NODES')
        key_t = decrypt(message, K3).decode('utf-8')
        if key_t == "K1":
            return encrypt(self.K1, K3)
        elif key_t == "K2":
            return encrypt(self.K1, K3)
        else:
            raise Exception("could not understand message")


if __name__ == '__main__':
    # disable_logging()
    lspy.ENABLE_LOGGING = True

    n = NodeNet()
    a = n.create_node(NodeA, PROTOCOL_OFB)
    b = n.create_node(NodeB)
    km = n.create_node(NodeKM)

    log('THE FILE THAT WE HAVE TO SEND IS: ', '"' + open('files/a.txt', 'r').read() + '"')

    a.start()
    b.start()
    km.start()

    a.join()
    b.join()
    km.join()
