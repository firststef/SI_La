from abc import ABC, abstractmethod
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable
from time import sleep

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

    def _request(self, node_name: str, request: str, *args, **kwargs):
        ss = socket(AF_INET, SOCK_STREAM)
        addr = self.dns.get_address_for(node_name)
        print(self.who() + ' trying to connect to ' + node_name)
        # sleep(1)
        ss.connect(addr)
        conn = ConnWrapper(ss)
        block = 0.1
        if 'block' in kwargs:
            block = kwargs.pop('block')
        rpc = RPC(stdin=conn, stdout=conn, block=block, initialize=False)
        res = rpc(request,  *args, **kwargs)
        print(self.who() + ' resolved request ' + request)
        if hasattr(rpc, 'watchdog'):
            print('CLIENT closed watchdog for request ' + request)
            rpc.watchdog.stop()
        return res

    def send_to(self, node_name: str, request: str, *args, **kwargs):
        """ Alias to request """
        self._request(node_name, request, *args, **kwargs)

    def request_from(self, node_name: str, request: str, *args, **kwargs):
        """ Alias to request """
        res = self._request(node_name, request, *args,  **kwargs)
        print(self.who() + ' got back ' + str(res))
        return res

    def register_dns(self, dns: NodeDNS):
        self.dns = dns

    def start(self):
        self.p.start()

    def join(self):
        self.p.join()

    def wait_one(self):
        self.wait_s = socket(AF_INET, SOCK_STREAM)
        self.wait_s.bind(self.dns.get_address_for(self.who()))
        self.wait_s.listen()
        print(self.who() + ' waiting for connection')
        self.conn, addr = self.wait_s.accept()
        print(self.who() + ' accepted connection')
        self.wrp = ConnWrapper(self.conn)
        self.rpc = RPC(target=self, stdin=self.wrp, stdout=self.wrp, initialize=False)

    @abstractmethod
    def serve(self):
        pass


def closeafter(func):
    def wrap(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        # print('Released watch dog for ' + self.who())
        print('HOST closing watchdog for request ' + func.__name__)
        try:
            self.rpc.watchdog.stop()
        except:
            pass
        print('HOST closed watchdog for request ' + func.__name__)
        return ret
    return wrap
