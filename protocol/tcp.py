from collections.abc import Callable
from socket import SocketType, socket, AF_INET, SOCK_STREAM
import threading
from asyncio import AbstractEventLoop
from typing import List
from logging import Logger

SOCKET_BUFFET_SIZE = 8192


class TCPServer():
    def __init__(
            self, logger: Logger, host: str = "0.0.0.0",
            port=6666, callback: Callable[[bytes], bytes] = lambda x: x
    ):
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
                connection = Connection(
                    self.logger, conn, addr,
                    lambda: self.connections.remove(connection), self.calback
                )
                self.connections.append(connection)
            except:
                pass

    def close(self):
        for connection in self.connections:
            connection.close()
            connection.thread.join()
        self.socket.close()


class Connection():
    def __init__(self, logger: Logger, conn: SocketType, addr,
                 on_close: Callable, callback: Callable[[bytes], bytes]
                 ):
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
        buf_bytes = bytearray()
        self.logger.debug(f"Server received size: {size}")

        if not size:
            return None
        size = int.from_bytes(size)

        for i in range(int(size / SOCKET_BUFFET_SIZE)):
            buf_bytes.extend(self.conn.recv(SOCKET_BUFFET_SIZE))

        buf_bytes.extend(self.conn.recv(size % SOCKET_BUFFET_SIZE))

        return buf_bytes

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
    def __init__(self, loop: AbstractEventLoop, host="localhost", port=6666):
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
        buf_bytes = bytearray()

        if not size:
            return None

        size = int.from_bytes(size)

        for i in range(int(size / SOCKET_BUFFET_SIZE)):
            buf_bytes.extend(await self.loop.sock_recv(
                self.socket, SOCKET_BUFFET_SIZE))

        buf_bytes.extend(await self.loop.sock_recv(
            self.socket, SOCKET_BUFFET_SIZE
        ))

        return buf_bytes

    def close(self):
        self.socket.close()
