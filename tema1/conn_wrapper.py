class ConnWrapper:
    def __init__(self, socket):
        self.socket = socket
        self.pos = 1

    def read(self, num):
        self.pos += num
        return self.socket.recv(num)

    def write(self, s):
        self.socket.sendall(s)

    def flush(self):
        pass

    def isatty(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, num):
        pass