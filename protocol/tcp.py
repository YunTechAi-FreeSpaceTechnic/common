from collections.abc import Callable
from socket import SocketType, socket, AF_INET, SOCK_STREAM
import selectors
from asyncio import AbstractEventLoop
from logging import Logger
import concurrent.futures

SOCKET_BUFFET_SIZE = 8192


class TCPServer():
    def __init__(
            self, logger: Logger, host: str = "0.0.0.0",
            port=6666, callback: Callable[[bytes], bytes] = lambda x: x
    ):
        self.port = port
        self.host = host
        self.calback = callback
        self.logger = logger
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.sel = selectors.DefaultSelector()
        self.is_close = False

        self.socket.bind((self.host, self.port))

    def listen(self):
        self.logger.info("Listening for connections...")
        self.socket.setblocking(False)
        self.socket.listen(100)
        self.sel.register(self.socket, selectors.EVENT_READ, data=None)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            while not self.is_close:
                events = self.sel.select(timeout=5)
                for key, _ in events:
                    if key.data is None:
                        self.accept_connections(executor)

    def accept_connections(self, executor: concurrent.futures.ThreadPoolExecutor):
        conn, addr = self.socket.accept()
        self.logger.info(f"Accepted connection from {addr}")
        conn.setblocking(False)
        executor.submit(Connection(self.logger, conn, addr, self.calback).listen)

class Connection():
    def __init__(self, logger: Logger, conn: SocketType, addr,
                 callback: Callable[[bytes], bytes]
                 ):
        self.logger = logger
        self.conn = conn
        self.addr = addr
        self.callback = callback

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

    def listen(self):
        data = self.recv()

        if not data:
            self.logger.info(f"Connection from {self.addr} closed.")
            return

        self.logger.debug(f"Server received data: {data}")

        try:
            self.send(self.callback(data))
        except:
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
