import base64
from socket import socket, AF_INET, SOCK_STREAM
from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable

from node_net_dns import NodeDNS
from lspy import RPC
from conn_wrapper import ConnWrapper


class Node(ABC):
    def __init__(self):
        self.p = Thread(target=self.serve)
        self.dns = None
        self.rpc = None
        self.wait_s = None
        self.conn = None
        self.wrp = None

    @abstractmethod
    def who(self) -> str:
        pass

    def request_from(self, node_name: str, request: str, r_bytes: bytes):
        ss = socket(AF_INET, SOCK_STREAM)
        addr = self.dns.get_address_for(node_name)
        ss.connect(addr)
        print(self.who() + ' connected to ', addr)
        conn = ConnWrapper(ss)
        ss.sendall(r_bytes)
        return None
        rpc = RPC(stdin=conn, stdout=conn, initialize=False)
        res = rpc(request, str(base64.b64encode(r_bytes)))
        print(self.who() + ' got response ', res)
        ss.close()
        return res

    def send_to(self, node_name: str, request: str, r_bytes: bytes):
        """ Alias to request_from """
        self.request_from(node_name, request, r_bytes)

    def respond_to(self, node_name: str, request: str, r_bytes: bytes):
        """ Alias to request_from """
        return self.request_from(node_name, request, r_bytes)

    def register_dns(self, dns: NodeDNS):
        self.dns = dns

    def start(self):
        self.p.start()

    def join(self):
        self.p.join()

    def wait_one(self, cb: Callable):
        self.wait_s = socket(AF_INET, SOCK_STREAM)
        self.wait_s.bind(self.dns.get_address_for(self.who()))
        self.wait_s.listen()
        self.conn, addr = self.wait_s.accept()
        print(self.who() + ' connected to ', addr)
        self.rpc = RPC(self)
        #self.rpc.watchdog.stop()  # this might be too soon

    @abstractmethod
    def serve(self):
        pass

