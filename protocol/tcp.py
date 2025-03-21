import asyncio
from collections.abc import Callable
from socket import SocketType, socket, AF_INET, SOCK_STREAM
import selectors
from asyncio import AbstractEventLoop
from logging import Logger
import concurrent.futures

SOCKET_BUFFET_SIZE = 8192


class TCPServer():

    def __init__(self,
                 logger: Logger,
                 host: str = "0.0.0.0",
                 port=6666,
                 callback: Callable[[bytearray], bytearray] = lambda x: x):
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

    def accept_connections(self,
                           executor: concurrent.futures.ThreadPoolExecutor):
        conn, addr = self.socket.accept()
        self.logger.info(f"Accepted connection from {addr}")
        conn.setblocking(False)
        executor.submit(
            Connection(self.logger, conn, addr, self.calback).listen)

    def close(self):
        self.is_close = True


class Connection():

    def __init__(self, logger: Logger, conn: socket, addr,
                 callback: Callable[[bytearray], bytearray]):
        self.logger = logger
        self.conn = conn
        self.addr = addr
        self.callback = callback
        self.loop = asyncio.new_event_loop()

    async def send(self, data):
        size = len(data)

        await self.loop.sock_sendall(self.conn, size.to_bytes(4))
        await self.loop.sock_sendall(self.conn, data)

    async def recv(self):
        buf_bytes = bytearray()
        size = await self.loop.sock_recv(self.conn, 4)
        self.logger.debug(f"Server received size: {size}")

        if not size:
            return None
        size = int.from_bytes(size)

        for _ in range(int(size / SOCKET_BUFFET_SIZE)):
            buf_bytes.extend(await self.loop.sock_recv(self.conn,
                                                       SOCKET_BUFFET_SIZE))

        buf_bytes.extend(await self.loop.sock_recv(self.conn,
                                                   size % SOCKET_BUFFET_SIZE))

        return buf_bytes

    def listen(self):
        asyncio.set_event_loop(self.loop)

        try:
            while True:
                data = asyncio.run(self.recv())

                if not data:
                    break

                self.logger.debug(f"Server received data: {data}")
                asyncio.run(self.send(self.callback(data)))
        finally:
            self.close()

    def close(self):
        self.logger.info(f"Connection from {self.addr} closed.")
        self.conn.close()


class TCPClient():

    def __init__(self, loop: AbstractEventLoop, host="localhost", port=6666):
        self.loop = loop
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((host, port))

    async def send(self, data: bytes) -> bytearray | None:
        size = len(data)
        await self.loop.sock_sendall(self.socket, size.to_bytes(4) + data)

        return await self.recv()

    async def recv(self):
        size = await self.loop.sock_recv(self.socket, 4)
        buf_bytes = bytearray()

        if not size:
            return None

        size = int.from_bytes(size)

        for _ in range(int(size / SOCKET_BUFFET_SIZE)):
            buf_bytes.extend(await self.loop.sock_recv(self.socket,
                                                       SOCKET_BUFFET_SIZE))

        buf_bytes.extend(await self.loop.sock_recv(self.socket,
                                                   SOCKET_BUFFET_SIZE))

        return buf_bytes

    def close(self):
        self.socket.close()
