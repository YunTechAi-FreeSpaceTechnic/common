from collections.abc import Callable
from socket import SocketType, socket, AF_INET, SOCK_STREAM
import threading
from asyncio import AbstractEventLoop
from typing import List
from logging import Logger

class TCPServer():
    def __init__(self, logger: Logger, host: str = "0.0.0.0",  port = 6666, callback: Callable[[bytes], bytes] = lambda x: x):
        self.port = port
        self.host = host
        self.calback = callback
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.connections: List[Connection] = []
        self.listen_thread.daemon = True
        self.logger = logger

    def listen(self):
        self.logger.info("Listening for connections...")
        self.socket.listen()
        self.socket.setblocking(False)

        while True:
            try:
                conn, addr = self.socket.accept()
                connection = Connection(self.logger, conn, addr, lambda: self.connections.remove(connection), self.calback)
                self.connections.append(connection)
            except:
                pass

    def close(self):
        for connection in self.connections:
            connection.close()
            connection.thread.join()
        self.socket.close()

class Connection():
    def __init__(self, logger: Logger, conn: SocketType, addr, on_close: Callable, callback: Callable[[bytes], bytes]):
        self.logger = logger
        self.conn = conn
        self.addr = addr
        self.callback = callback
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.on_close = on_close
        self.thread.start()

    def send(self, data):
        size = len(data)

        self.conn.send(size.to_bytes(4))
        self.conn.send(data)

    def recv(self):
        size = self.conn.recv(4)
        self.logger.debug(f"Server received size: {size}")

        if not size:
            return None

        return self.conn.recv(int.from_bytes(size))
    def close(self):
        self.conn.close()
        self.on_close()


    def listen(self):
        data = self.recv()

        if not data:
            self.logger.info(f"Connection from {self.addr} closed.")
            self.on_close()
            return

        self.logger.debug(f"Server received data: {data}")

        try:
            self.send(self.callback(data))
            self.on_close()
        except:
            self.on_close()
            return

class TCPClient():
    def __init__(self, loop: AbstractEventLoop, host = "localhost", port = 6666):
        self.loop = loop
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((host, port))

    async def send(self, data: bytes) -> bytes | None:
        size = len(data)

        await self.loop.sock_sendall(self.socket, size.to_bytes(4) + data)

        return await self.recv()

    async def recv(self):
        size = await self.loop.sock_recv(self.socket, 4)

        if not size:
            return None

        return await self.loop.sock_recv(self.socket, int.from_bytes(size))

    def close(self):
        self.socket.close()
