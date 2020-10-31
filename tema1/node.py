from abc import ABC, abstractmethod
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable

from conn_wrapper import ConnWrapper
from lspy import RPC
from node_net_dns import NodeDNS


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

    def request_from(self, node_name: str, request: str,  message: str):
        ss = socket(AF_INET, SOCK_STREAM)
        addr = self.dns.get_address_for(node_name)
        ss.connect(addr)
        print(self.who() + ' connected to ', addr)
        conn = ConnWrapper(ss)
        rpc = RPC(stdin=conn, stdout=conn, initialize=False)
        res = rpc(request, message)
        print(self.who() + ' got response ', res)
        rpc.watchdog.stop()
        return res

    def send_to(self, node_name: str, request: str, message: str):
        """ Alias to request_from """
        self.request_from(node_name, request, message)

    def respond_to(self, node_name: str, request: str,  message: str):
        """ Alias to request_from """
        return self.request_from(node_name, request,  message)

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
        self.wrp = ConnWrapper(self.conn)
        self.rpc = RPC(target=self, stdin=self.wrp, stdout=self.wrp, initialize=False)

    @abstractmethod
    def serve(self):
        pass


def closeafter(func):
    def wrap(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        self.rpc.watchdog.stop()
        return ret
    return wrap