class ConnWrapper:
    def __init__(self, socket):
        self.socket = socket
        self.pos = 1

    def read(self, num):
        try:
            return self.socket.recv(num)
        except:
            raise OSError

    def write(self, s):
        try:
            self.socket.sendall(s)
        except:
            return

    def flush(self):
        pass

    def isatty(self):
        return True

    def tell(self):
        self.pos += 1
        return self.pos

    def seek(self, num):
        pass